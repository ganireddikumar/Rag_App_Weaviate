import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import axios from 'axios';

const Chat = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState('');
  const [question, setQuestion] = useState('');
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    if (selectedDocument) {
      fetchConversations();
    }
  }, [selectedDocument]);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/documents');
      setDocuments(response.data);
      if (response.data.length > 0) {
        setSelectedDocument(response.data[0].id);
      }
    } catch (err) {
      setError('Error fetching documents');
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/conversations?document_id=${selectedDocument}`);
      setConversations(response.data);
    } catch (err) {
      setError('Error fetching conversations');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || !selectedDocument) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        question,
        document_id: selectedDocument,
      });

      setConversations([response.data, ...conversations]);
      setQuestion('');
    } catch (err) {
      setError(err.response?.data?.error || 'Error sending question');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Select Document</InputLabel>
          <Select
            value={selectedDocument}
            onChange={(e) => setSelectedDocument(e.target.value)}
            label="Select Document"
          >
            {documents.map((doc) => (
              <MenuItem key={doc.id} value={doc.id}>
                {doc.filename}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about the document..."
              disabled={!selectedDocument}
            />
            <Button
              type="submit"
              variant="contained"
              disabled={!selectedDocument || !question.trim() || loading}
            >
              {loading ? <CircularProgress size={24} /> : <SendIcon />}
            </Button>
          </Box>
        </form>

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
      </Paper>

      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Conversation History
        </Typography>
        <List>
          {conversations.map((conv, index) => (
            <ListItem key={index} divider>
              <ListItemText
                primary={
                  <Typography variant="subtitle1" color="primary">
                    Q: {conv.question}
                  </Typography>
                }
                secondary={
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    A: {conv.answer}
                  </Typography>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default Chat; 