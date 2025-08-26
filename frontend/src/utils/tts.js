class GestureSpeaker {
  constructor() {
    this.synth = window.speechSynthesis;
    this.voices = [];
    this.voice = null;
    this.isReady = false;
    
    // Load voices when they become available
    this.synth.onvoiceschanged = this.loadVoices.bind(this);
    this.loadVoices();
  }

  loadVoices() {
    this.voices = this.synth.getVoices();
    // Try to find a good default voice
    this.voice = this.voices.find(voice => 
      voice.lang.startsWith('en-') && 
      voice.name.includes('English') &&
      voice.localService
    ) || null;
    this.isReady = !!this.voice;
    
    if (!this.isReady && this.voices.length > 0) {
      // Fallback to first available voice
      this.voice = this.voices[0];
      this.isReady = true;
    }
    
    console.log('Available voices:', this.voices);
    console.log('Using voice:', this.voice);
  }

  speak(text) {
    if (!this.isReady || !this.voice) {
      console.warn('TTS not ready or no voice available');
      return false;
    }

    // Stop any current speech
    this.synth.cancel();

    // Create and speak the utterance
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = this.voice;
    utterance.pitch = 1;
    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.volume = 1;

    this.synth.speak(utterance);
    return true;
  }

  // Helper method to speak a letter
  speakLetter(letter) {
    return this.speak(letter);
  }

  // Helper method to speak a word
  speakWord(word) {
    return this.speak(word);
  }
}

export default GestureSpeaker;
