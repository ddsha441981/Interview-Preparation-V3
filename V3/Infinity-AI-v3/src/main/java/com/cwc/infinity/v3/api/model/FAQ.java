package com.cwc.infinity.v3.api.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import org.springframework.data.annotation.Id;
import org.springframework.data.elasticsearch.annotations.Document;

@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@Builder
@Document(indexName = "faq")
public class FAQ {

    @Id
    private String id;
    @JsonProperty("question")
    private String question;
    @JsonProperty("answer")
    private String answer;
}

