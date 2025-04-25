import React from 'react';
import { ChakraProvider, Box } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import Chat from './components/Chat';
import Navbar from './components/Navbar';

const App: React.FC = () => {
  return (
    <ChakraProvider>
      <Router>
        <Box minH="100vh" bg="gray.50">
          <Navbar />
          <Box maxW="1200px" mx="auto" p={4}>
            <Routes>
              <Route path="/" element={<FileUpload />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ChakraProvider>
  );
};

export default App; 