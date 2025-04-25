import React from 'react';
import { Box, Flex, Link, Text } from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();

  return (
    <Box bg="blue.500" px={4} py={3}>
      <Flex maxW="1200px" mx="auto" align="center" justify="space-between">
        <Text fontSize="xl" color="white" fontWeight="bold">
          Document Chat
        </Text>
        <Flex gap={6}>
          <Link
            as={RouterLink}
            to="/"
            color="white"
            fontWeight={location.pathname === '/' ? 'bold' : 'normal'}
            _hover={{ textDecoration: 'none', opacity: 0.8 }}
          >
            File Upload
          </Link>
          <Link
            as={RouterLink}
            to="/chat"
            color="white"
            fontWeight={location.pathname === '/chat' ? 'bold' : 'normal'}
            _hover={{ textDecoration: 'none', opacity: 0.8 }}
          >
            Chat
          </Link>
        </Flex>
      </Flex>
    </Box>
  );
};

export default Navbar; 