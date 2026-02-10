// src/store/index.js
import { createStore } from 'vuex'
import apiService from '@/services/api' // Use @ to reference the src folder

export default createStore({
  state: {
    statusMessage: '',
    taskId: null,
    isLoading: false,
    messages: [],
    activeTicker: '',
    isProcessingDocument: false,
    processedTickers: []
  },
  mutations: {
    SET_LOADING(state, isLoading) {
      state.isLoading = isLoading;
    },
    SET_ACTIVE_TICKER(state, ticker) {
        state.activeTicker = ticker;
        state.messages = [{ sender: 'ai', text: `Hello! How can I help you research ${ticker}?` }];
    },
    ADD_MESSAGE(state, message) {
        state.messages.push(message);
    },
    SET_DOC_PROCESSING(state, isProcessing) { // <-- ADD THIS
        state.isProcessingDocument = isProcessing;
    },
    ADD_PROCESSED_TICKER(state, ticker) { // <-- ADD THIS MUTATION
        if (!state.processedTickers.includes(ticker)) {
            state.processedTickers.push(ticker);
        }
    }
  },
  actions: {
    // eslint-disable-next-line
    async askQuestion({ commit, state }, payload) {
      const { question, ticker } = payload;
      commit('ADD_MESSAGE', { sender: 'user', text: question });
      commit('SET_LOADING', true);

      try {
        const response = await apiService.post('/api/query', { question, ticker });
        commit('ADD_MESSAGE', { sender: 'ai', text: response.data.answer });
      } catch (error) {
        console.error("Error querying the API:", error);
        commit('ADD_MESSAGE', { sender: 'ai', text: 'Sorry, I ran into an error. Please try again.' });
      } finally {
        commit('SET_LOADING', false);
      }
    }
  }
})