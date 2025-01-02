package com.cwc.infinity.v3.api.controller;

import com.cwc.infinity.v3.api.model.FAQ;
import com.cwc.infinity.v3.api.service.KnowledgeBaseService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v3/interview/ai")
@Slf4j
@RequiredArgsConstructor
public class FAQController {

    private final KnowledgeBaseService knowledgeBaseService;

    @GetMapping("/test")
    public String testLogging() {
        log.info("This is an INFO message");
        log.warn("This is a WARN message");
        log.error("This is an ERROR message");
        return "Logging test completed";
    }

    @PostMapping("/indexFaqs")
    public String indexFaqs(@RequestBody List<FAQ> faqList) {
        for (FAQ faq : faqList) {
            knowledgeBaseService.indexQuestionAnswer(faq.getQuestion(), faq.getAnswer());
        }
        return "FAQs indexed successfully!";
    }
}
