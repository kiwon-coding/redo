<template>
  <div class="crop-editor">
    <div class="crop-container" ref="containerRef">
      <img
        ref="imageRef"
        :src="imageUrl"
        alt="Crop image"
        class="crop-image"
        @load="onImageLoad"
        draggable="false"
      />

      <!-- Overlay: crop 영역 외부 어둡게 -->
      <div v-if="cropArea" class="crop-overlay">
        <!-- Crop 영역 (밝게 표시) -->
        <div
          class="crop-area"
          :style="cropAreaStyle"
          @mousedown="startMove"
          @touchstart="startMove"
        >
          <!-- Corner handles -->
          <div
            class="crop-handle crop-handle-tl"
            @mousedown.stop="startResize($event, 'tl')"
            @touchstart.stop="startResize($event, 'tl')"
          ></div>
          <div
            class="crop-handle crop-handle-tr"
            @mousedown.stop="startResize($event, 'tr')"
            @touchstart.stop="startResize($event, 'tr')"
          ></div>
          <div
            class="crop-handle crop-handle-bl"
            @mousedown.stop="startResize($event, 'bl')"
            @touchstart.stop="startResize($event, 'bl')"
          ></div>
          <div
            class="crop-handle crop-handle-br"
            @mousedown.stop="startResize($event, 'br')"
            @touchstart.stop="startResize($event, 'br')"
          ></div>

          <!-- Edge handles -->
          <div
            class="crop-handle crop-handle-t"
            @mousedown.stop="startResize($event, 't')"
            @touchstart.stop="startResize($event, 't')"
          ></div>
          <div
            class="crop-handle crop-handle-b"
            @mousedown.stop="startResize($event, 'b')"
            @touchstart.stop="startResize($event, 'b')"
          ></div>
          <div
            class="crop-handle crop-handle-l"
            @mousedown.stop="startResize($event, 'l')"
            @touchstart.stop="startResize($event, 'l')"
          ></div>
          <div
            class="crop-handle crop-handle-r"
            @mousedown.stop="startResize($event, 'r')"
            @touchstart.stop="startResize($event, 'r')"
          ></div>
        </div>
      </div>
    </div>

    <div class="crop-controls">
      <button
        @click="handleConfirm"
        :disabled="!cropArea || isProcessing"
        class="confirm-button"
      >
        {{ isProcessing ? "처리 중..." : "Crop 확인" }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";

interface Props {
  imageId: string;
  imageUrl: string;
}

interface CropArea {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface CropResponse {
  file_id: string;
  stored_path: string;
  original_image_id: string;
  crop: { x: number; y: number; w: number; h: number };
}

type ResizeHandle = "tl" | "tr" | "bl" | "br" | "t" | "b" | "l" | "r" | null;

type DragMode = "resize" | "move" | null;

const props = defineProps<Props>();
const emit = defineEmits<{
  "crop-confirmed": [response: CropResponse];
}>();

const containerRef = ref<HTMLDivElement | null>(null);
const imageRef = ref<HTMLImageElement | null>(null);

const originalImageWidth = ref<number>(0);
const originalImageHeight = ref<number>(0);
const displayImageWidth = ref<number>(0);
const displayImageHeight = ref<number>(0);

const cropArea = ref<CropArea | null>(null);
const dragMode = ref<DragMode>(null);
const resizeHandle = ref<ResizeHandle>(null);
const dragStart = ref<{ x: number; y: number; cropArea: CropArea } | null>(
  null
);
const isProcessing = ref<boolean>(false);

// 이미지 로드 완료 시 원본 크기 저장 및 초기 crop 영역 설정
const onImageLoad = () => {
  if (imageRef.value) {
    // 원본 이미지 크기 가져오기
    originalImageWidth.value = imageRef.value.naturalWidth;
    originalImageHeight.value = imageRef.value.naturalHeight;

    // 화면에 표시된 이미지 크기
    displayImageWidth.value = imageRef.value.clientWidth;
    displayImageHeight.value = imageRef.value.clientHeight;

    // 초기 crop 영역을 전체 이미지로 설정
    cropArea.value = {
      x: 0,
      y: 0,
      width: displayImageWidth.value,
      height: displayImageHeight.value,
    };
  }
};

// 좌표를 원본 이미지 기준으로 변환
const toOriginalCoordinates = (
  displayX: number,
  displayY: number,
  displayW: number,
  displayH: number
) => {
  const scaleX = originalImageWidth.value / displayImageWidth.value;
  const scaleY = originalImageHeight.value / displayImageHeight.value;

  return {
    x: Math.round(displayX * scaleX),
    y: Math.round(displayY * scaleY),
    w: Math.round(displayW * scaleX),
    h: Math.round(displayH * scaleY),
  };
};

// 화면 좌표 가져오기 (터치/마우스 공통)
const getEventCoordinates = (
  e: MouseEvent | TouchEvent
): { x: number; y: number } => {
  if ("touches" in e) {
    const touch = e.touches[0] || e.changedTouches[0];
    if (!touch) return { x: 0, y: 0 };
    const rect = containerRef.value?.getBoundingClientRect();
    if (rect) {
      return {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top,
      };
    }
  } else {
    const rect = containerRef.value?.getBoundingClientRect();
    if (rect) {
      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    }
  }
  return { x: 0, y: 0 };
};

// 이미지 내부 좌표로 변환
const toImageCoordinates = (coords: { x: number; y: number }) => {
  if (!imageRef.value) return { x: 0, y: 0 };

  const rect = imageRef.value.getBoundingClientRect();
  const containerRect = containerRef.value?.getBoundingClientRect();
  if (!containerRect) return { x: 0, y: 0 };

  const imageX = rect.left - containerRect.left;
  const imageY = rect.top - containerRect.top;

  return {
    x: coords.x - imageX,
    y: coords.y - imageY,
  };
};

// 이미지 경계 내부로 제한
const clampToImage = (x: number, y: number, w: number, h: number) => {
  const maxX = displayImageWidth.value;
  const maxY = displayImageHeight.value;

  // 위치 제한
  x = Math.max(0, Math.min(x, maxX - w));
  y = Math.max(0, Math.min(y, maxY - h));

  // 크기 제한
  w = Math.max(20, Math.min(w, maxX - x));
  h = Math.max(20, Math.min(h, maxY - y));

  return { x, y, width: w, height: h };
};

// Resize 시작
const startResize = (e: MouseEvent | TouchEvent, handle: ResizeHandle) => {
  e.preventDefault();
  e.stopPropagation();

  if (!cropArea.value) return;

  const coords = getEventCoordinates(e);
  dragMode.value = "resize";
  resizeHandle.value = handle;
  dragStart.value = {
    x: coords.x,
    y: coords.y,
    cropArea: { ...cropArea.value },
  };
};

// Move 시작
const startMove = (e: MouseEvent | TouchEvent) => {
  e.preventDefault();

  if (!cropArea.value) return;

  const coords = getEventCoordinates(e);
  const imgCoords = toImageCoordinates(coords);

  // crop 영역 내부인지 확인
  const { x, y, width, height } = cropArea.value;
  if (
    imgCoords.x >= x &&
    imgCoords.x <= x + width &&
    imgCoords.y >= y &&
    imgCoords.y <= y + height
  ) {
    dragMode.value = "move";
    resizeHandle.value = null;
    dragStart.value = {
      x: coords.x,
      y: coords.y,
      cropArea: { ...cropArea.value },
    };
  }
};

// 드래그 중
const onDrag = (e: MouseEvent | TouchEvent) => {
  if (!dragMode.value || !dragStart.value || !cropArea.value) return;

  e.preventDefault();
  const coords = getEventCoordinates(e);
  const imgCoords = toImageCoordinates(coords);
  const imgDeltaX = imgCoords.x - toImageCoordinates(dragStart.value).x;
  const imgDeltaY = imgCoords.y - toImageCoordinates(dragStart.value).y;

  const start = dragStart.value.cropArea;
  let newArea: CropArea;

  if (dragMode.value === "move") {
    // 영역 이동
    newArea = {
      x: start.x + imgDeltaX,
      y: start.y + imgDeltaY,
      width: start.width,
      height: start.height,
    };
  } else if (dragMode.value === "resize" && resizeHandle.value) {
    // 핸들로 크기 조정
    const handle = resizeHandle.value;
    let x = start.x;
    let y = start.y;
    let width = start.width;
    let height = start.height;

    // 모서리 핸들
    if (handle === "tl") {
      x = start.x + imgDeltaX;
      y = start.y + imgDeltaY;
      width = start.width - imgDeltaX;
      height = start.height - imgDeltaY;
    } else if (handle === "tr") {
      y = start.y + imgDeltaY;
      width = start.width + imgDeltaX;
      height = start.height - imgDeltaY;
    } else if (handle === "bl") {
      x = start.x + imgDeltaX;
      width = start.width - imgDeltaX;
      height = start.height + imgDeltaY;
    } else if (handle === "br") {
      width = start.width + imgDeltaX;
      height = start.height + imgDeltaY;
    }
    // 가장자리 핸들
    else if (handle === "t") {
      y = start.y + imgDeltaY;
      height = start.height - imgDeltaY;
    } else if (handle === "b") {
      height = start.height + imgDeltaY;
    } else if (handle === "l") {
      x = start.x + imgDeltaX;
      width = start.width - imgDeltaX;
    } else if (handle === "r") {
      width = start.width + imgDeltaX;
    }

    // 크기가 음수가 되면 위치와 크기를 조정
    if (width < 0) {
      x += width;
      width = Math.abs(width);
    }
    if (height < 0) {
      y += height;
      height = Math.abs(height);
    }

    newArea = { x, y, width, height };
  } else {
    return;
  }

  // 이미지 경계 내부로 제한
  cropArea.value = clampToImage(
    newArea.x,
    newArea.y,
    newArea.width,
    newArea.height
  );
};

// 드래그 종료
const endDrag = (e: MouseEvent | TouchEvent) => {
  if (!dragMode.value) return;

  e.preventDefault();
  dragMode.value = null;
  resizeHandle.value = null;
  dragStart.value = null;
};

// 이벤트 리스너 등록
onMounted(() => {
  window.addEventListener("mousemove", onDrag);
  window.addEventListener("mouseup", endDrag);
  window.addEventListener("touchmove", onDrag, { passive: false });
  window.addEventListener("touchend", endDrag, { passive: false });
});

// 이벤트 리스너 제거
onUnmounted(() => {
  window.removeEventListener("mousemove", onDrag);
  window.removeEventListener("mouseup", endDrag);
  window.removeEventListener("touchmove", onDrag);
  window.removeEventListener("touchend", endDrag);
});

// Crop 영역 스타일
const cropAreaStyle = computed(() => {
  if (!cropArea.value || !imageRef.value) return {};

  const rect = imageRef.value.getBoundingClientRect();
  const containerRect = containerRef.value?.getBoundingClientRect();
  if (!containerRect) return {};

  const imageX = rect.left - containerRect.left;
  const imageY = rect.top - containerRect.top;

  return {
    left: `${imageX + cropArea.value.x}px`,
    top: `${imageY + cropArea.value.y}px`,
    width: `${cropArea.value.width}px`,
    height: `${cropArea.value.height}px`,
  };
});

// Crop 확인 버튼 클릭
const handleConfirm = async () => {
  if (!cropArea.value || !imageRef.value || isProcessing.value) return;

  isProcessing.value = true;

  try {
    // 원본 이미지 기준 좌표로 변환
    const originalCoords = toOriginalCoordinates(
      cropArea.value.x,
      cropArea.value.y,
      cropArea.value.width,
      cropArea.value.height
    );

    // Backend API 호출
    const response = await fetch("http://127.0.0.1:8000/crop", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image_id: props.imageId,
        crop: {
          x: originalCoords.x,
          y: originalCoords.y,
          w: originalCoords.w,
          h: originalCoords.h,
        },
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Crop failed");
    }

    const data: CropResponse = await response.json();

    // 부모 컴포넌트에 결과 전달
    emit("crop-confirmed", data);
  } catch (error) {
    console.error("Crop error:", error);
    alert(
      `Crop 실패: ${error instanceof Error ? error.message : "Unknown error"}`
    );
  } finally {
    isProcessing.value = false;
  }
};
</script>

<style scoped>
.crop-editor {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem;
}

.crop-container {
  position: relative;
  display: inline-block;
  max-width: 100%;
  user-select: none;
  -webkit-user-select: none;
  touch-action: none;
}

.crop-image {
  display: block;
  max-width: 100%;
  max-height: 70vh;
  height: auto;
  pointer-events: none;
}

.crop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  pointer-events: none;
}

.crop-area {
  position: absolute;
  background-color: transparent;
  border: 2px solid #4caf50;
  /* box-shadow로 crop 영역 외부를 어둡게 처리 */
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
  cursor: move;
  pointer-events: all;
}

.crop-handle {
  position: absolute;
  background-color: #4caf50;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  pointer-events: all;
  cursor: pointer;
  /* iPhone 터치 타겟 최소 44px */
  min-width: 44px;
  min-height: 44px;
}

/* Corner handles */
.crop-handle-tl,
.crop-handle-tr,
.crop-handle-bl,
.crop-handle-br {
  border-radius: 50%;
  width: 44px;
  height: 44px;
}

.crop-handle-tl {
  top: -22px;
  left: -22px;
  cursor: nwse-resize;
}

.crop-handle-tr {
  top: -22px;
  right: -22px;
  cursor: nesw-resize;
}

.crop-handle-bl {
  bottom: -22px;
  left: -22px;
  cursor: nesw-resize;
}

.crop-handle-br {
  bottom: -22px;
  right: -22px;
  cursor: nwse-resize;
}

/* Edge handles */
.crop-handle-t,
.crop-handle-b {
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 44px;
  border-radius: 22px;
}

.crop-handle-t {
  top: -22px;
  cursor: ns-resize;
}

.crop-handle-b {
  bottom: -22px;
  cursor: ns-resize;
}

.crop-handle-l,
.crop-handle-r {
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 60px;
  border-radius: 22px;
}

.crop-handle-l {
  left: -22px;
  cursor: ew-resize;
}

.crop-handle-r {
  right: -22px;
  cursor: ew-resize;
}

.crop-controls {
  display: flex;
  gap: 1rem;
}

.confirm-button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  min-height: 44px; /* iPhone 터치 타겟 */
}

.confirm-button:hover:not(:disabled) {
  background-color: #45a049;
}

.confirm-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* iPhone Safari 대응: 터치 스크롤 방지 */
@media (hover: none) and (pointer: coarse) {
  .crop-container {
    -webkit-overflow-scrolling: touch;
    overflow: hidden;
  }

  .crop-handle {
    /* 터치 디바이스에서 더 큰 타겟 */
    min-width: 48px;
    min-height: 48px;
  }

  .crop-handle-tl,
  .crop-handle-tr,
  .crop-handle-bl,
  .crop-handle-br {
    width: 48px;
    height: 48px;
  }

  .crop-handle-t,
  .crop-handle-b {
    width: 64px;
    height: 48px;
  }

  .crop-handle-l,
  .crop-handle-r {
    width: 48px;
    height: 64px;
  }
}
</style>
