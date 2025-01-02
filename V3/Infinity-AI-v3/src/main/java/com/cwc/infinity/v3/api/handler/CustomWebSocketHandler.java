package com.cwc.infinity.v3.api.handler;

import com.cwc.infinity.v3.api.service.KnowledgeBaseService;
import lombok.extern.slf4j.Slf4j;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.net.URI;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

@Service
@Slf4j
public class CustomWebSocketHandler extends TextWebSocketHandler {


    @Autowired
    private KnowledgeBaseService knowledgeBaseService;



    @Override
    public void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String receivedText = message.getPayload();
        log.debug("Received text: {}", receivedText);
        System.out.println("-------------------" + receivedText);
        String cachedAnswer = knowledgeBaseService.getAnswer(receivedText);


        if (cachedAnswer != null) {
            // Send cached answer back to React
            session.sendMessage(new TextMessage(cachedAnswer));
            return;
        }

        CountDownLatch latch = new CountDownLatch(1);

        try {
            WebSocketClient client = new WebSocketClient(new URI("ws://localhost:5000")) {
                @Override
                public void onOpen(ServerHandshake serverHandshake) {
                    log.debug("WebSocket opened: {}", serverHandshake);
                    try {
                        this.send(receivedText);
                    } catch (Exception e) {
                        log.error("Error sending message", e);
                        latch.countDown();
                    }
                }

                @Override
                public void onMessage(String message) {
                    log.debug("Received message from server: {}", message);

                    if (message == null || message.trim().isEmpty()) {
                        log.warn("Received blank or invalid response. Keeping the connection open.");
                        return;
                    }

                    try {
                        // Index the new question and answer in Elasticsearch
                        knowledgeBaseService.indexQuestionAnswer(receivedText, message);

                        // Send the response back to the original WebSocket client (React)
                        session.sendMessage(new TextMessage(message));
                    } catch (Exception e) {
                        log.error("Error handling message", e);
                    } finally {
                        latch.countDown();
                    }
                }

                @Override
                public void onClose(int code, String reason, boolean remote) {
                    log.debug("WebSocket closed with exit code {} and reason {}", code, reason);
                    latch.countDown();
                }

                @Override
                public void onError(Exception ex) {
                    log.error("WebSocket error", ex);
                    latch.countDown();
                }
            };

            client.connectBlocking();

            if (!latch.await(10, TimeUnit.SECONDS)) {
                log.warn("No response from server within timeout. Closing connection.");
                client.closeBlocking();
            }

        } catch (Exception e) {
            log.error("Error handling text message", e);
        }
    }
}
