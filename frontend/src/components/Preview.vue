<template>
  <div class="preview">
    <h2 class="title">Crop 결과 미리보기</h2>

    <div class="preview-container">
      <img
        :src="getImageUrl(cropResult)"
        :alt="'Crop preview'"
        class="preview-image"
        @error="handleImageError"
      />
    </div>

    <div class="actions">
      <button @click="handleAnalyze" class="analyze-button">분석하기</button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface CropResult {
  file_id: string;
  stored_path: string;
  original_image_id: string;
  crop: { x: number; y: number; w: number; h: number };
}

interface Props {
  cropResult: CropResult;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  analyze: [];
}>();

// 이미지 URL 가져오기
const getImageUrl = (crop: CropResult): string => {
  // Backend의 /files/{file_id} 엔드포인트를 사용
  return `http://127.0.0.1:8000/files/${crop.file_id}`;
};

// 이미지 로드 에러 처리
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.src =
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23ddd' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999'%3E이미지 없음%3C/text%3E%3C/svg%3E";
};

// 분석하기 버튼 클릭
const handleAnalyze = () => {
  emit("analyze");
};
</script>

<style scoped>
.preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 1rem;
}

.title {
  text-align: center;
  color: #333;
  margin: 0;
  font-size: 1.5rem;
}

.preview-container {
  width: 100%;
  max-width: 600px;
  border: 2px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  display: block;
}

.actions {
  display: flex;
  justify-content: center;
  width: 100%;
}

.analyze-button {
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  /* iPhone 터치 타겟 */
  min-height: 44px;
}

.analyze-button:hover {
  background-color: #0b7dda;
}

.analyze-button:active {
  transform: scale(0.98);
}

/* iPhone Safari 대응 */
@media (hover: none) and (pointer: coarse) {
  .preview-container {
    min-height: 250px;
  }
}
</style>
