<template>
  <div class="search-bar-container">
    <InputText 
      v-model="ticker" 
      placeholder="Enter stock ticker (e.g., AAPL)" 
      @keyup.enter="onSearch"
    />
    <PButton 
      label="Search" 
      icon="pi pi-search" 
      @click="onSearch"
      :disabled="!ticker"
    />
  </div>
</template>

<script>
import InputText from 'primevue/inputtext';

export default {
  name: 'SearchBar',
  components: {
    InputText
  },
  data() {
    return {
      ticker: ''
    };
  },
  methods: {
    onSearch() {
      if (this.ticker.trim()) {
        this.$emit('search-ticker', this.ticker.trim().toUpperCase());
        this.ticker = '';
      }
    }
  }
}
</script>

<style scoped>
.search-bar-container {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 1rem;
}
</style>