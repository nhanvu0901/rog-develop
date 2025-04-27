import React, {useState, useRef, useEffect, useCallback} from 'react';
import {
    Box,
    VStack,
    Input,
    Button,
    Text,
    HStack,
    Flex,
    useToast,
} from '@chakra-ui/react';
import useWebSocket, {ReadyState} from 'react-use-websocket';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'ws://localhost:8000/api/v1/chat';

interface Message {
    text: string;
    isUser: boolean;
}

const Chat = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const toast = useToast();

    const {sendMessage, lastMessage, readyState} = useWebSocket(SOCKET_URL, {
        onOpen: () => {
            toast({
                title: 'Connected',
                status: 'success',
                duration: 2000,
            });
        },
        onError: () => {
            toast({
                title: 'Connection failed',
                status: 'error',
                duration: 2000,
            });
        },
        //Tự động kết nối lại khi mất kết nối
        shouldReconnect: () => true,
    });

    // Loading indicator animation
    const [loadingDots, setLoadingDots] = useState('.');
    useEffect(() => {
        let dotInterval: NodeJS.Timeout;
        if (isLoading) {
            dotInterval = setInterval(() => {
                setLoadingDots(prev => {
                    if (prev === '.') return '..';
                    if (prev === '..') return '...';
                    return '.';
                });
            }, 500);
        }
        return () => {
            if (dotInterval) clearInterval(dotInterval);
        };
    }, [isLoading]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({behavior: "smooth"});
    };

    useEffect(() => {
        if (lastMessage !== null) {
            try {
                const data = JSON.parse(lastMessage.data);
                const botMessage: Message = {
                    text: data.response,
                    isUser: false,
                };
                setMessages(prev => [...prev, botMessage]);
                setIsLoading(false);
            } catch (err) {
                console.error('Failed to parse message:', err);
                setIsLoading(false);
            }
        }
    }, [lastMessage]);

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const formatMessage = (text: string) => {
        return text.split('\n\n').map((paragraph: string, paragraphIndex: number) => {
            const lines = paragraph.split('\n');

            if (lines.length === 1) {
                return (
                    <Text key={paragraphIndex} mb={paragraphIndex < text.split('\n\n').length - 1 ? 3 : 0}>
                        {paragraph}
                    </Text>
                );
            }
            return (
                <Text key={paragraphIndex} mb={paragraphIndex < text.split('\n\n').length - 1 ? 3 : 0}>
                    {lines.map((line: string, lineIndex: number) => (
                        <React.Fragment key={lineIndex}>
                            {line}
                            {lineIndex < lines.length - 1 && <br/>}
                        </React.Fragment>
                    ))}
                </Text>
            );
        });
    };

    const handleSend = useCallback(() => {
        if (!input.trim()) return;
        if (readyState !== ReadyState.OPEN) {
            toast({
                title: 'Connection not ready',
                status: 'warning',
                duration: 2000,
            });
            return;
        }

        const userMessage: Message = {
            text: input,
            isUser: true,
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        // Gửi tin nhắn dưới dạng JSON string
        sendMessage(JSON.stringify({text: input}));
        setInput('');
    }, [input, sendMessage, readyState, toast]);

    // Hiển thị trạng thái kết nối
    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Connected',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState];

    return (
        <VStack spacing={4} align="stretch">
            <Text fontSize="sm" color={readyState === ReadyState.OPEN ? 'green.500' : 'red.500'}>
                Status: {connectionStatus}
            </Text>
            <Box
                p={4}
                borderWidth={1}
                borderRadius="lg"
                bg="white"
                height="60vh"
                overflowY="auto"
            >
                <VStack spacing={4} align="stretch">
                    {messages.map((message, index) => (
                        <Flex
                            key={index}
                            justify={message.isUser ? "flex-end" : "flex-start"}
                        >
                            <Box
                                bg={message.isUser ? "blue.500" : "gray.100"}
                                color={message.isUser ? "white" : "black"}
                                p={3}
                                borderRadius="lg"
                                maxW="80%"
                                position="relative"
                                _after={message.isUser ? {
                                    content: '""',
                                    position: "absolute",
                                    right: "-8px",
                                    top: "50%",
                                    transform: "translateY(-50%)",
                                    border: "8px solid transparent",
                                    borderLeftColor: "blue.500"
                                } : undefined}
                                _before={!message.isUser ? {
                                    content: '""',
                                    position: "absolute",
                                    left: "-8px",
                                    top: "50%",
                                    transform: "translateY(-50%)",
                                    border: "8px solid transparent",
                                    borderRightColor: "gray.100"
                                } : undefined}
                            >
                                <Text>{formatMessage(message.text)}</Text>
                            </Box>
                        </Flex>
                    ))}

                    {/* Loading animation */}
                    {isLoading && (
                        <Flex justify="flex-start">
                            <Box
                                bg="gray.100"
                                color="black"
                                p={3}
                                borderRadius="lg"
                                maxW="80%"
                                position="relative"
                                _before={{
                                    content: '""',
                                    position: "absolute",
                                    left: "-8px",
                                    top: "50%",
                                    transform: "translateY(-50%)",
                                    border: "8px solid transparent",
                                    borderRightColor: "gray.100"
                                }}
                            >
                                <Text fontWeight="bold">{loadingDots}</Text>
                            </Box>
                        </Flex>
                    )}

                    <div ref={messagesEndRef}/>
                </VStack>
            </Box>
            <HStack>
                <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                            handleSend();
                        }
                    }}
                    isDisabled={readyState !== ReadyState.OPEN || isLoading}
                />
                <Button
                    colorScheme="blue"
                    onClick={handleSend}
                    isDisabled={readyState !== ReadyState.OPEN || isLoading}
                    isLoading={isLoading}
                    loadingText="Sending"
                >
                    Send
                </Button>
            </HStack>
        </VStack>
    );
};

export default Chat;