import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Generate unique session ID
const generateSessionId = () => {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

const ChatMessage = ({ message, isUser }) => (
  <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
      isUser 
        ? 'bg-blue-500 text-white' 
        : 'bg-gray-100 text-gray-800'
    }`}>
      <p className="text-sm">{message}</p>
    </div>
  </div>
);

const DrugCard = ({ drug }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
    <h3 className="font-semibold text-lg text-gray-800 mb-2">{drug.name}</h3>
    <p className="text-sm text-gray-600 mb-2">{drug.generic_name}</p>
    <p className="text-sm text-gray-700 mb-3">{drug.description}</p>
    
    <div className="mb-2">
      <span className="font-medium text-green-600">Uses: </span>
      <span className="text-sm text-gray-600">{drug.uses.join(', ')}</span>
    </div>
    
    <div className="mb-2">
      <span className="font-medium text-blue-600">Dosage: </span>
      <span className="text-sm text-gray-600">{drug.dosage}</span>
    </div>
    
    <div className="mb-2">
      <span className="font-medium text-orange-600">Side Effects: </span>
      <span className="text-sm text-gray-600">{drug.side_effects.join(', ')}</span>
    </div>
    
    <div>
      <span className="font-medium text-red-600">Precautions: </span>
      <span className="text-sm text-gray-600">{drug.precautions.join(', ')}</span>
    </div>
  </div>
);

const SearchResults = ({ results, onClose }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div className="bg-white rounded-lg max-w-4xl w-full max-h-96 overflow-y-auto">
      <div className="p-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-xl font-semibold">Search Results</h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>
      <div className="p-4">
        {results.length === 0 ? (
          <p className="text-gray-500">No drugs found matching your search.</p>
        ) : (
          <div className="grid gap-4">
            {results.map((drug) => (
              <DrugCard key={drug.id} drug={drug} />
            ))}
          </div>
        )}
      </div>
    </div>
  </div>
);

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(generateSessionId());
  const [drugSuggestions, setDrugSuggestions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initial greeting
    setMessages([
      {
        text: "Hello! I'm MediAid, your local health assistant. I can help you with information about medications and basic health advice. What symptoms are you experiencing?",
        isUser: false
      }
    ]);
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message to chat
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);

    try {
      const response = await axios.post(`${API}/chat`, {
        session_id: sessionId,
        message: userMessage
      });

      // Add bot response to chat
      setMessages(prev => [...prev, { text: response.data.response, isUser: false }]);
      
      // Update drug suggestions
      setDrugSuggestions(response.data.drug_suggestions || []);
      
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        text: 'Sorry, I encountered an error. Please try again.', 
        isUser: false 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const searchDrugs = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const response = await axios.get(`${API}/search?query=${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data);
      setShowSearchResults(true);
    } catch (error) {
      console.error('Error searching drugs:', error);
      setSearchResults([]);
      setShowSearchResults(true);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">🏥</span>
              </div>
              <div className="ml-3">
                <h1 className="text-2xl font-bold text-gray-900">MediAid</h1>
                <p className="text-sm text-gray-600">Local Drug Finder & Health Advice</p>
              </div>
            </div>
            
            {/* Search Bar */}
            <form onSubmit={searchDrugs} className="flex">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search drugs by name or symptom..."
                className="px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={isSearching}
                className="px-4 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {isSearching ? '🔍...' : '🔍'}
              </button>
            </form>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chat Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-96 flex flex-col">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-800">Health Chat Assistant</h2>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4">
                {messages.map((message, index) => (
                  <ChatMessage
                    key={index}
                    message={message.text}
                    isUser={message.isUser}
                  />
                ))}
                {isLoading && (
                  <div className="flex justify-start mb-4">
                    <div className="bg-gray-100 text-gray-800 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                      <p className="text-sm">Thinking...</p>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
              
              <form onSubmit={sendMessage} className="p-4 border-t border-gray-200">
                <div className="flex">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Ask about symptoms, medications, or health advice..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-6 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    Send
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Drug Suggestions Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800">Drug Suggestions</h3>
              </div>
              <div className="p-4">
                {drugSuggestions.length === 0 ? (
                  <p className="text-gray-500 text-sm">
                    Ask about your symptoms to get personalized drug suggestions.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {drugSuggestions.map((drug) => (
                      <div key={drug.id} className="border border-gray-200 rounded-lg p-3">
                        <h4 className="font-medium text-gray-800">{drug.name}</h4>
                        <p className="text-sm text-gray-600 mb-2">{drug.description}</p>
                        <div className="text-xs text-gray-500">
                          <span className="font-medium">Uses: </span>
                          {drug.uses.join(', ')}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          <span className="font-medium">Dosage: </span>
                          {drug.dosage}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Health Tips */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 mt-6">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800">Health Tips</h3>
              </div>
              <div className="p-4">
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Always consult a healthcare provider for serious conditions</li>
                  <li>• Take medications as prescribed</li>
                  <li>• Stay hydrated and get adequate rest</li>
                  <li>• Don't exceed recommended dosages</li>
                  <li>• Keep a list of your medications</li>
                  <li>• Report any adverse reactions</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search Results Modal */}
      {showSearchResults && (
        <SearchResults
          results={searchResults}
          onClose={() => setShowSearchResults(false)}
        />
      )}
    </div>
  );
}

export default App;