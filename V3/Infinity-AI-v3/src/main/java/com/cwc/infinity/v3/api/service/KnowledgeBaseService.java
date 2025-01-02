package com.cwc.infinity.v3.api.service;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.search.Hit;
import co.elastic.clients.elasticsearch.indices.GetIndexRequest;
import co.elastic.clients.elasticsearch.indices.GetIndexResponse;
import com.cwc.infinity.v3.api.model.FAQ;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.text.Normalizer;
import java.util.Locale;
@Service
@Slf4j
@RequiredArgsConstructor
public class KnowledgeBaseService {

    private final ElasticsearchClient elasticsearchClient;

    private final StringRedisTemplate redisTemplate;

    private static final String CACHE_PREFIX = "FAQ_";

    private String normalize(String input) {
        String normalized = Normalizer.normalize(input, Normalizer.Form.NFD);
        normalized = normalized.replaceAll("\\p{M}", "");
        normalized = normalized.replaceAll("[^\\w\\s]", "");
        return normalized.trim().toLowerCase(Locale.ROOT);
    }

    private String generateCacheKey(String question) {
        String normalizedQuestion = normalize(question);
        int hash = question.hashCode();
        return CACHE_PREFIX + normalizedQuestion + "_" + hash;
    }

    public String getAnswer(String question) {
        log.debug("Received question: {}", question);
        String cacheKey = generateCacheKey(question);

        // Check Redis cache first
        String cachedAnswer = redisTemplate.opsForValue().get(cacheKey);
        if (cachedAnswer != null) {
            log.debug("Answer found in cache for question: {}", cacheKey);
            return cachedAnswer;
        }

        // If not found in cache, query Elasticsearch
        String answer = getAnswerFromKnowledgeBase(normalize(question));
        if (answer != null) {
            redisTemplate.opsForValue().set(cacheKey, answer);
        }

        return answer;
    }

    private String getAnswerFromKnowledgeBase(String normalizedQuestion) {
        int retryCount = 3;
        int retryDelay = 5000;

        for (int i = 0; i < retryCount; i++) {
            try {
                if (!checkIndexExists("faq")) {
                    log.error("Index 'faq' does not exist.");
                    return null;
                }

                SearchRequest searchRequest = new SearchRequest.Builder()
                        .index("faq")
                        .query(q -> q
                                .matchPhrase(m -> m
                                        .field("question")
                                        .query(normalizedQuestion)
                                )
                        )
                        .build();

                SearchResponse<FAQ> searchResponse = elasticsearchClient.search(searchRequest, FAQ.class);

                if (searchResponse.hits().hits().isEmpty()) {
                    log.debug("No hits found for question: {}", normalizedQuestion);
                    return null;
                } else {
                    Hit<FAQ> hit = searchResponse.hits().hits().get(0);
                    return hit.source().getAnswer();
                }
            } catch (Exception e) {
                log.error("Error retrieving answer from knowledge base, retrying... attempt {}", i + 1, e);
                try {
                    Thread.sleep(retryDelay);
                    retryDelay *= 2;
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    log.error("Retry interrupted", ie);
                    break;
                }
            }
        }

        log.error("Failed to retrieve answer from knowledge base after {} attempts", retryCount);
        return null;
    }

    public void indexQuestionAnswer(String question, String answer) {
        try {
            String cacheKey = generateCacheKey(question);
            FAQ faq = new FAQ();
            faq.setQuestion(question); // Store the original question
            faq.setAnswer(answer);

            elasticsearchClient.index(i -> i
                    .index("faq")
                    .id(cacheKey)
                    .document(faq)
            );

            redisTemplate.opsForValue().set(cacheKey, answer);
            log.debug("Indexed question-answer pair in Elasticsearch and cache: {}", cacheKey);
        } catch (Exception e) {
            log.error("Error indexing question-answer pair", e);
        }
    }

    private boolean checkIndexExists(String indexName) {
        try {
            GetIndexRequest getIndexRequest = new GetIndexRequest.Builder()
                    .index(indexName)
                    .build();
            GetIndexResponse getIndexResponse = elasticsearchClient.indices().get(getIndexRequest);

            return getIndexResponse.result().containsKey(indexName);
        } catch (Exception e) {
            log.error("Error checking if index exists", e);
            return false;
        }
    }
}