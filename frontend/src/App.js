import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container, Box } from '@mui/material';
import Upload from './components/Upload';
import Chat from './components/Chat';

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              RAG Application
            </Typography>
            <Button color="inherit" component={Link} to="/">
              Upload
            </Button>
            <Button color="inherit" component={Link} to="/chat">
              Chat
            </Button>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Routes>
            <Route path="/" element={<Upload />} />
            <Route path="/chat" element={<Chat />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
}

export default App; 