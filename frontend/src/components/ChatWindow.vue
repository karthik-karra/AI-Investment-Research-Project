<template>
  <div class="chat-container">
    <div v-if="isProcessing" class="processing-overlay">
      <i class="pi pi-spin pi-cog" style="font-size: 3rem"></i>
      <p>Analyzing company documents... This may take a minute.</p>
    </div>

    <div v-else class="messages-area">
      <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.sender]">
        <p>{{ msg.text }}</p>
      </div>
    </div>

    <div class="input-area">
      <InputText
        v-model="userQuestion"
        placeholder="Ask a question..."
        @keyup.enter="sendQuestion"
        :disabled="!activeTicker || isLoading || isProcessing"
        style="flex-grow: 1;"
      />
      <PButton
        icon="pi pi-send"
        @click="sendQuestion"
        :disabled="!userQuestion || isLoading || isProcessing"
      />
      <div v-if="isLoading" class="spinner-container">
        <i class="pi pi-spinner pi-spin" style="font-size: 1.5rem"></i>
      </div>
    </div>
  </div>
</template>

<script>
import InputText from 'primevue/inputtext';
import Button from 'primevue/button'; // <-- ADD THIS IMPORT

export default {
  name: 'ChatWindow',
  components: {
    InputText,
    PButton: Button // <-- REGISTER THE COMPONENT
  },
  props: {
    messages: {
      type: Array,
      required: true
    },
    activeTicker: {
        type: String,
        default: ''
    },
    isLoading: {
        type: Boolean,
        default: false
    },
    isProcessing: {
        type: Boolean,
        default: false
    }
  },
  data() {
    return {
      userQuestion: ''
    };
  },
  methods: {
    sendQuestion() {
      if (this.userQuestion.trim()) {
        this.$emit('send-question', this.userQuestion.trim());
        this.userQuestion = '';
      }
    }
  }
}
</script>

<style scoped>
.messages-area {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 1rem;
  margin-bottom: 1rem;
}
.message {
  margin-bottom: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  max-width: 80%;
}
.message.user {
  background-color: #007bff;
  color: white;
  align-self: flex-end;
  margin-left: auto;
}
.message.ai {
  background-color: #e9ecef;
  color: #495057;
  align-self: flex-start;
}
.input-area {
    display: flex;
    gap: 0.5rem;
    align-items: center; /* Vertically align items */
}
.spinner-container {
    width: 40px; /* Give it a fixed width */
    text-align: center;
}
.input-area > * {
  flex-grow: 1;
}
.processing-overlay {
    height: 400px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #6c757d;
}
</style>