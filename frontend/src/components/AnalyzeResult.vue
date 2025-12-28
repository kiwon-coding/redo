<template>
  <div class="analyze-result">
    <h2 class="title">분석 결과</h2>

    <!-- 문제 이미지 -->
    <div class="problem-image-container">
      <img
        :src="getProblemImageUrl()"
        alt="문제 이미지"
        class="problem-image"
        @error="handleImageError"
      />
    </div>

    <!-- 답안 표시 및 수정 -->
    <div class="answer-section">
      <label class="answer-label">정답:</label>
      <input
        v-model="answerText"
        type="text"
        class="answer-input"
        placeholder="정답을 입력하세요"
      />
      <span class="confidence" v-if="confidence > 0">
        (신뢰도: {{ (confidence * 100).toFixed(1) }}%)
      </span>
    </div>

    <!-- 액션 버튼 -->
    <div class="actions">
      <button
        @click="handleConfirm"
        :disabled="isConfirming || !answerText.trim()"
        class="confirm-button"
      >
        {{ isConfirming ? "저장 중..." : "확인" }}
      </button>
      <button @click="handleRecrop" class="recrop-button">다시 crop</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

interface AnalyzeResponse {
  message: string;
  file_id: string;
  problem_image_url: string;
  answer: {
    text: string;
    confidence: number;
  };
}

interface Props {
  cropFileId: string;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  confirmed: [answer: string];
  recrop: [];
}>();

const problemImageUrl = ref<string>("");
const problemImageFileId = ref<string>("");
const answerText = ref<string>("");
const confidence = ref<number>(0);
const isProcessing = ref<boolean>(false);
const isConfirming = ref<boolean>(false);

// 분석 실행
onMounted(async () => {
  await runAnalyze();
});

const runAnalyze = async () => {
  isProcessing.value = true;
  try {
    const response = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        file_id: props.cropFileId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Analysis failed");
    }

    const data: AnalyzeResponse = await response.json();
    problemImageUrl.value = data.problem_image_url;
    problemImageFileId.value = data.problem_image_file_id;
    answerText.value = data.answer.text;
    confidence.value = data.answer.confidence;
  } catch (error) {
    console.error("Analyze error:", error);
    alert(
      `분석 실패: ${error instanceof Error ? error.message : "Unknown error"}`
    );
  } finally {
    isProcessing.value = false;
  }
};

// 문제 이미지 URL 가져오기
const getProblemImageUrl = (): string => {
  if (!problemImageUrl.value) return "";
  // URL이 상대 경로인 경우 절대 경로로 변환
  if (problemImageUrl.value.startsWith("/")) {
    return `http://127.0.0.1:8000${problemImageUrl.value}`;
  }
  return problemImageUrl.value;
};

// 이미지 로드 에러 처리
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.src =
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23ddd' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999'%3E이미지 없음%3C/text%3E%3C/svg%3E";
};

// 확인 버튼 클릭
const handleConfirm = async () => {
  if (!problemImageFileId.value || !answerText.value.trim()) {
    alert("답안을 입력해주세요.");
    return;
  }

  isConfirming.value = true;
  try {
    const response = await fetch("http://127.0.0.1:8000/problems", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        problem_image_file_id: problemImageFileId.value,
        answer_value: answerText.value,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Problem save failed");
    }

    const data = await response.json();
    console.log("Problem saved:", data);

    // 부모 컴포넌트에 확인 이벤트 전달
    emit("confirmed", answerText.value);
  } catch (error) {
    console.error("Save problem error:", error);
    alert(
      `저장 실패: ${error instanceof Error ? error.message : "Unknown error"}`
    );
  } finally {
    isConfirming.value = false;
  }
};

// 다시 crop 버튼 클릭
const handleRecrop = () => {
  emit("recrop");
};
</script>

<style scoped>
.analyze-result {
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

.problem-image-container {
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

.problem-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  display: block;
}

.answer-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  max-width: 600px;
  flex-wrap: wrap;
}

.answer-label {
  font-weight: bold;
  color: #333;
  font-size: 1.1rem;
}

.answer-input {
  flex: 1;
  min-width: 200px;
  padding: 0.75rem;
  font-size: 1.1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  min-height: 44px; /* iPhone 터치 타겟 */
}

.answer-input:focus {
  outline: none;
  border-color: #2196f3;
}

.confidence {
  color: #666;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 1rem;
  width: 100%;
  max-width: 600px;
  justify-content: center;
}

.confirm-button,
.recrop-button {
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  min-height: 44px; /* iPhone 터치 타겟 */
}

.confirm-button {
  background-color: #4caf50;
  color: white;
}

.confirm-button:hover {
  background-color: #45a049;
}

.recrop-button {
  background-color: #ff9800;
  color: white;
}

.recrop-button:hover {
  background-color: #f57c00;
}

.confirm-button:active,
.recrop-button:active {
  transform: scale(0.98);
}

.confirm-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.confirm-button:disabled:active {
  transform: none;
}

/* iPhone Safari 대응 */
@media (hover: none) and (pointer: coarse) {
  .problem-image-container {
    min-height: 250px;
  }
}
</style>
