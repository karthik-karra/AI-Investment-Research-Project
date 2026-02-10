<template>
  <div id="app" class="app-container">
    <header class="app-header">
      <h1>CogniVest</h1>
      <p>AI-Powered Investment Research</p>
    </header>

    <main class="app-main">
      <PCard>
        <template #title>
          <h2>Research Assistant</h2>
        </template>
        <template #content>
          <SearchBar @search-ticker="handleSearch" />
          <div v-if="activeTicker" class="active-ticker-display">
            <p>Now researching: <strong>{{ activeTicker }}</strong></p>
            <StockChart :chartData="chartData" />
          </div>
          <ChatWindow 
            :messages="messages" 
            :activeTicker="activeTicker"
            :isLoading="isLoading"
            :isProcessing="isProcessingDocument"
            @send-question="handleSendQuestion" 
          />
        </template>
      </PCard>
    </main>

    <footer class="app-footer">
      <p>&copy; 2025 CogniVest. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import apiService from './services/api';
import Card from 'primevue/card';
import SearchBar from './components/SearchBar.vue';
import ChatWindow from './components/ChatWindow.vue';
import StockChart from './components/StockChart.vue';

export default {
  name: 'App',
  components: {
    PCard: Card,
    SearchBar,
    ChatWindow,
    StockChart
  },
  data() {
    return {
      chartData: []
    };
  },
  computed: {
    ...mapState(['activeTicker', 'messages', 'isLoading', 'isProcessingDocument', 'processedTickers'])
  },
  // In frontend/src/App.vue
  methods: {
    ...mapActions(['askQuestion']),

    // This function will poll the backend for the task status
    pollTaskStatus(taskId, ticker) {
        const interval = setInterval(async () => {
            try {
                const response = await apiService.get(`/task-status/${taskId}`);
                console.log(`Polling for ${ticker}: Status is ${response.data.status}`);

                if (response.data.status === 'SUCCESS') {
                    clearInterval(interval);
                    console.log(`Processing complete for ${ticker}. Adding a small delay for DB to sync.`);

                    // --- THIS IS THE FIX ---
                    // Add a 2-second buffer to ensure the database has time to commit the data
                    setTimeout(() => {
                        this.$store.commit('ADD_PROCESSED_TICKER', ticker);
                        this.$store.commit('SET_DOC_PROCESSING', false);
                        console.log("Buffer time complete. Ready to query.");
                    }, 2000); // 2000 milliseconds = 2 seconds
                    // ---------------------

                } else if (response.data.status === 'FAILURE') {
                    clearInterval(interval);
                    this.$store.commit('SET_DOC_PROCESSING', false);
                    console.error(`Processing failed for ${ticker}.`);
                }
            } catch (error) {
                clearInterval(interval);
                this.$store.commit('SET_DOC_PROCESSING', false);
                console.error("Error during task polling:", error);
            }
        }, 5000); // Check every 5 seconds
    },

    async handleSearch(ticker) {
      this.$store.commit('SET_ACTIVE_TICKER', ticker);
      this.chartData = [];

      try {
        const response = await apiService.post('/process-document', { ticker });

        if (response.data.message === "Documents already processed.") {
          console.log(`Ticker ${ticker} has already been processed. Ready to query.`);
          this.$store.commit('ADD_PROCESSED_TICKER', ticker);
          this.$store.commit('SET_DOC_PROCESSING', false);
        } else {
          // If processing was newly initiated, start polling for its status
          console.log(`Processing initiated for new ticker: ${ticker}...`);
          this.$store.commit('SET_DOC_PROCESSING', true);
          this.pollTaskStatus(response.data.task_id, ticker);
        }

        // Fetch chart data immediately
        const chartResponse = await apiService.get(`/api/stock-data/${ticker}`);
        if (chartResponse.data && !chartResponse.data.error) {
          this.chartData = chartResponse.data.data;
        }
      } catch (error) {
        console.error("Error during search handling:", error);
        this.$store.commit('SET_DOC_PROCESSING', false);
      }
    },
    handleSendQuestion(question) {
      if (this.isProcessingDocument) {
          alert("Please wait for the document analysis to complete before asking questions.");
          return;
      }
      this.askQuestion({ question: question, ticker: this.activeTicker });
    }
  }
}
</script>

<style>
/* Add any new styles if needed, the old ones are fine */
body {
  background-color: #f8f9fa;
  margin: 0;
}
.app-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1rem;
}
.app-header, .app-footer {
  text-align: center;
  color: #495057;
}
.active-ticker-display {
    text-align: center;
    margin: -1rem 0 1rem 0;
    font-style: italic;
}
</style>