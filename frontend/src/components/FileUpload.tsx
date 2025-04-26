import React, {useState, useRef, useEffect} from 'react';
import {
    Box,
    Button,
    Input,
    VStack,
    Text,
    useToast,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    Icon,
    Center,
    Flex,
    Spinner,
    Modal,
    ModalOverlay,
    ModalContent
} from '@chakra-ui/react';
import {FiFile, FiClock, FiTrash2, FiUploadCloud} from 'react-icons/fi';

interface FileInfo {
    filename: string;
    size: number;
    uploaded_at: string;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const ALLOW_EDEXTENSIONS = ['pdf', 'docx', 'pptx', 'xlsx', 'csv', 'txt'];

const FileUpload = () => {
    const [file, setFile] = useState<File | null>(null);
    const [uploadedFiles, setUploadedFiles] = useState<FileInfo[]>([]);
    const [isDragOver, setIsDragOver] = useState(false);
    const toast = useToast();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isloading, setIsLoading] = useState(false)

    const fetchFiles = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`${API_URL}/files`);
            if (response.ok) {
                const files = await response.json();
                setUploadedFiles(files);
            }
        } catch (error) {
            console.error('Error fetching files:', error);
            toast({
                title: 'Failed to fetch files',
                description: 'Please try again later',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchFiles();
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
            if (ALLOW_EDEXTENSIONS.includes(fileExtension)) {
                processFile(file);
            } else {
                setIsDragOver(false);
                toast({
                    title: 'Unsupported File Type',
                    description: `Only ${ALLOW_EDEXTENSIONS.join(', ')} files are allowed.`,
                    status: 'warning',
                })
            }
        }
    };

    const processFile = async (selectedFile: File) => {
        setFile(selectedFile);
        await uploadFile(selectedFile);
    };

    const resetForm = () => {
        setFile(null);
        setIsDragOver(false);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const formatDate = (dateString: string): string => {
        return new Date(dateString).toLocaleString();
    };

    const uploadFile = async (fileToUpload: File) => {
        setIsLoading(true);
        const formData = new FormData();
        formData.append('file', fileToUpload);

        try {
            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                toast({
                    title: 'File uploaded successfully',
                    status: 'success',
                    duration: 3000,
                    isClosable: true,
                });
                resetForm();
                fetchFiles(); // Refresh file list
            } else if (response && response.status === 400) {
                const errorData = await response.json();
                toast({
                    title: 'Upload failed',
                    description: errorData.detail,
                    status: 'error',
                    duration: 3000,
                    isClosable: true,
                });
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            toast({
                title: 'Upload failed',
                description: "Please try again",
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
        }
        finally {
            setIsLoading(false);
        }
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(true);
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(false);
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();

        const droppedFiles = e.dataTransfer.files;
        if (droppedFiles.length > 0) {
            const file = droppedFiles[0];
            const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';

            if (ALLOW_EDEXTENSIONS.includes(fileExtension)) {
                processFile(file);
            } else {
                setIsDragOver(false);
                toast({
                    title: 'Unsupported File Type',
                    description: `Only ${ALLOW_EDEXTENSIONS.join(', ')} files are allowed.`,
                    status: 'warning',
                    duration: 3000,
                    isClosable: true,
                });
            }
        } else {
            setIsDragOver(false);
        }
    };

    const handleDelete = async (filename: string) => {
        try {
            const response = await fetch(`${API_URL}/files/${filename}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                toast({
                    title: 'File deleted successfully',
                    status: 'success',
                    duration: 3000,
                    isClosable: true,
                });
                fetchFiles(); // Refresh file list
            } else {
                throw new Error('Delete failed');
            }
        } catch (error) {
            toast({
                title: 'Delete failed',
                description: 'Please try again',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
        }
    };

    return (
        <VStack spacing={4} align="stretch">
            <Modal isOpen={isloading} onClose={() => {
            }} isCentered closeOnOverlayClick={false}>
                <ModalOverlay/>
                <ModalContent bg="transparent" boxShadow="none" display="flex" alignItems="center"
                              justifyContent="center">
                    <VStack>
                        <Spinner size="xl" color="blue.500" thickness="4px"/>
                        <Text color="white" fontWeight="bold" mt={4}>Loading...</Text>
                    </VStack>
                </ModalContent>
            </Modal>
            <Box
                p={6}
                borderWidth={1}
                borderRadius="lg"
                bg="white"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                position="relative"
                borderColor={isDragOver ? "blue.500" : "gray.200"}
                borderStyle="dashed"
                transition="all 0.3s"
            >
                <VStack spacing={4}>
                    <Text fontSize="xl" fontWeight="bold">Upload File</Text>
                    <Input
                        ref={fileInputRef}
                        type="file"
                        onChange={handleFileChange}
                        accept={"." + ALLOW_EDEXTENSIONS.join(',.')}
                        position="absolute"
                        top="0"
                        left="0"
                        opacity="0"
                        width="full"
                        height="full"
                        cursor="pointer"
                    />
                    <Center
                        width="full"
                        height="200px"
                        border="2px dashed"
                        borderColor={isDragOver ? "blue.500" : "gray.200"}
                        borderRadius="lg"
                        transition="all 0.3s"
                    >
                        <VStack>
                            <Icon
                                as={FiUploadCloud}
                                w={12}
                                h={12}
                                color={isDragOver ? "blue.500" : "gray.400"}
                                transition="all 0.3s"
                            />
                            <Text color={isDragOver ? "blue.500" : "gray.500"}>
                                {isDragOver
                                    ? "Drop file here"
                                    : "Drag and drop files here or click to select: ." + ALLOW_EDEXTENSIONS.join(', .')}
                            </Text>
                        </VStack>
                    </Center>
                </VStack>
            </Box>

            {file && (
                <Box p={4} bg="blue.50" borderRadius="lg">
                    <Flex align="center" justify="space-between">
                        <Flex align="center">
                            <Icon as={FiFile} mr={2}/>
                            <Text>{file.name}</Text>
                        </Flex>
                        <Text>{formatFileSize(file.size)}</Text>
                    </Flex>
                </Box>
            )}

            {uploadedFiles.length > 0 && (
                <Box p={6} borderWidth={1} borderRadius="lg" bg="white">
                    <Text fontSize="lg" fontWeight="bold" mb={4}>Uploaded Files</Text>
                    <Table variant="simple">
                        <Thead>
                            <Tr>
                                <Th>Name</Th>
                                <Th>Size</Th>
                                <Th>Upload Date</Th>
                                <Th>Actions</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {uploadedFiles.map((uploadedFile) => (
                                <Tr key={uploadedFile.filename}>
                                    <Td>
                                        <Icon as={FiFile} mr={2}/>
                                        {uploadedFile.filename}
                                    </Td>
                                    <Td>{formatFileSize(uploadedFile.size)}</Td>
                                    <Td>
                                        <Icon as={FiClock} mr={2}/>
                                        {formatDate(uploadedFile.uploaded_at)}
                                    </Td>
                                    <Td>
                                        <Icon
                                            as={FiTrash2}
                                            cursor="pointer"
                                            color="red.500"
                                            onClick={() => handleDelete(uploadedFile.filename)}
                                        />
                                    </Td>
                                </Tr>
                            ))}
                        </Tbody>
                    </Table>
                </Box>
            )}
        </VStack>
    );
};

export default FileUpload; 