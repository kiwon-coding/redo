<template>
  <div class="app-container">
    <h1>초등 수학 오답 관리</h1>

    <!-- 1단계: 이미지 업로드 -->
    <ImageUpload
      v-if="currentStep === 'upload'"
      @upload-success="handleUploadSuccess"
    />

    <!-- 2단계: Crop Editor -->
    <CropEditor
      v-if="currentStep === 'crop' && originalImageId && originalImageUrl"
      :image-id="originalImageId"
      :image-url="originalImageUrl"
      @crop-confirmed="handleCropConfirmed"
    />

    <!-- 3단계: Preview -->
    <Preview
      v-if="currentStep === 'preview' && currentCropResult"
      :crop-result="currentCropResult"
      @analyze="handleAnalyze"
    />

    <!-- 4단계: Analyze Result -->
    <AnalyzeResult
      v-if="currentStep === 'analyze' && currentCropResult"
      :crop-file-id="currentCropResult.file_id"
      @confirmed="handleAnalyzeConfirmed"
      @recrop="handleRecrop"
    />

    <!-- 에러 메시지 -->
    <p v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
// @ts-ignore - Vue SFC components
import ImageUpload from "./components/ImageUpload.vue";
// @ts-ignore - Vue SFC components
import CropEditor from "./components/CropEditor.vue";
// @ts-ignore - Vue SFC components
import Preview from "./components/Preview.vue";
// @ts-ignore - Vue SFC components
import AnalyzeResult from "./components/AnalyzeResult.vue";

type Step = "upload" | "crop" | "preview" | "analyze";

// 현재 단계
const currentStep = ref<Step>("upload");

// 원본 이미지 정보
const originalImageId = ref<string | null>(null);
const originalImageUrl = ref<string | null>(null);

// 현재 Crop 결과
const currentCropResult = ref<{
  file_id: string;
  stored_path: string;
  original_image_id: string;
  crop: { x: number; y: number; w: number; h: number };
} | null>(null);

// 에러 메시지
const errorMessage = ref<string>("");

// 업로드 성공 핸들러
const handleUploadSuccess = (data: { fileId: string; imageUrl: string }) => {
  originalImageId.value = data.fileId;
  originalImageUrl.value = data.imageUrl;
  currentStep.value = "crop";
  errorMessage.value = "";
};

// Crop 확인 핸들러
const handleCropConfirmed = (response: {
  file_id: string;
  stored_path: string;
  original_image_id: string;
  crop: { x: number; y: number; w: number; h: number };
}) => {
  // 현재 Crop 결과 저장
  currentCropResult.value = response;

  // Preview 단계로 이동
  currentStep.value = "preview";
  errorMessage.value = "";
};

// 분석하기 핸들러
const handleAnalyze = () => {
  if (!currentCropResult.value) return;

  // Analyze 단계로 이동
  currentStep.value = "analyze";
  errorMessage.value = "";
};

// 분석 결과 확인 핸들러
const handleAnalyzeConfirmed = (answer: string) => {
  console.log("Problem saved with answer:", answer);
  // 문제가 저장되었으므로 초기 상태로 리셋
  // TODO: 문제 리스트 화면으로 이동하거나 다음 단계로 진행
  alert(`문제가 저장되었습니다. 정답: "${answer}"`);

  // 초기 상태로 리셋 (선택사항)
  // currentStep.value = "upload";
  // currentCropResult.value = null;
  // originalImageId.value = null;
  // originalImageUrl.value = null;
};

// 다시 crop 핸들러
const handleRecrop = () => {
  if (!currentCropResult.value) return;

  // 원본 이미지 정보 복원
  // original_image_id를 사용하여 원본 이미지 URL 재생성
  const originalId = currentCropResult.value.original_image_id;

  if (originalId) {
    originalImageId.value = originalId;
    // 원본 이미지 URL 재생성 (backend에서 가져오기)
    originalImageUrl.value = `http://127.0.0.1:8000/files/${originalId}`;
  }

  // Crop 단계로 돌아가기
  currentStep.value = "crop";
  errorMessage.value = "";
};
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

.error-message {
  color: red;
  margin-top: 1rem;
  text-align: center;
}
</style>
