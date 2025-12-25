<template>
  <div class="app-container">
    <h1>초등 수학 오답 관리</h1>

    <div class="upload-section">
      <!-- 파일 선택 input -->
      <input
        type="file"
        ref="fileInputRef"
        @change="handleFileSelect"
        accept="image/*"
        style="display: none"
      />

      <!-- 파일 선택 버튼 -->
      <button @click="fileInputRef?.click()" class="select-button">
        이미지 선택
      </button>

      <!-- 선택한 이미지 미리보기 -->
      <div v-if="selectedImage" class="preview-container">
        <img
          :src="selectedImage"
          alt="선택한 이미지 미리보기"
          class="preview-image"
        />
        <p class="file-name">{{ fileName }}</p>
      </div>

      <!-- 업로드 버튼 -->
      <button
        v-if="selectedImage"
        @click="handleUpload"
        class="upload-button"
        :disabled="isUploading"
      >
        {{ isUploading ? "업로드 중..." : "업로드" }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from "vue";

// 파일 input 요소에 대한 참조
const fileInputRef = ref<HTMLInputElement | null>(null);

// 선택한 File 객체
const selectedFile = ref<File | null>(null);

// 선택한 이미지의 미리보기 URL (blob URL)
const selectedImage = ref<string | null>(null);

// 업로드 중 상태
const isUploading = ref<boolean>(false);

// 파일 이름은 selectedFile에서 계산
const fileName = computed(() => selectedFile.value?.name || "");

// 파일 선택 시 호출되는 함수
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];

  if (!file) {
    return;
  }

  // 이전에 생성한 URL이 있다면 메모리 해제
  if (selectedImage.value) {
    URL.revokeObjectURL(selectedImage.value);
  }

  // File 객체 저장
  selectedFile.value = file;

  // URL.createObjectURL을 사용하여 미리보기 URL 생성
  selectedImage.value = URL.createObjectURL(file);
};

// 업로드 버튼 클릭 시 호출되는 함수
const handleUpload = async () => {
  if (!selectedFile.value) {
    return;
  }

  isUploading.value = true;

  try {
    // TODO: 실제 업로드 로직 구현
    // 예: API 호출하여 서버에 이미지 전송
    console.log("업로드할 파일:", selectedFile.value.name);

    // 임시로 1초 대기 (실제로는 API 호출)
    await new Promise((resolve) => setTimeout(resolve, 1000));

    alert("업로드 완료!");

    // 업로드 후 초기화
    resetSelection();
  } catch (error) {
    console.error("업로드 실패:", error);
    alert("업로드에 실패했습니다.");
  } finally {
    isUploading.value = false;
  }
};

// 선택 초기화 함수
const resetSelection = () => {
  // blob URL 메모리 해제
  if (selectedImage.value) {
    URL.revokeObjectURL(selectedImage.value);
  }

  selectedFile.value = null;
  selectedImage.value = null;

  // input 요소 초기화
  if (fileInputRef.value) {
    fileInputRef.value.value = "";
  }
};

// 컴포넌트 언마운트 시 메모리 정리
onUnmounted(() => {
  if (selectedImage.value) {
    URL.revokeObjectURL(selectedImage.value);
  }
});
</script>

<style scoped>
.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.select-button,
.upload-button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.select-button {
  background-color: #4caf50;
  color: white;
}

.select-button:hover {
  background-color: #45a049;
}

.upload-button {
  background-color: #2196f3;
  color: white;
}

.upload-button:hover:not(:disabled) {
  background-color: #0b7dda;
}

.upload-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px dashed #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.file-name {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}
</style>
