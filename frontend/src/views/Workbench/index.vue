<template>
  <div class="workbench-page">
    <section class="input-panel">
      <h1 class="panel-title">📝 原始作业输入</h1>
      <el-input
        v-model="text"
        class="source-textarea"
        type="textarea"
        resize="vertical"
        placeholder="粘贴微信群老师作业文本...&#10;apple 苹果&#10;banana 香蕉&#10;beautiful 美丽的"
      />

      <div class="divider" />

      <el-form label-width="104px" class="setting-form">
        <el-form-item label="标题">
          <el-input v-model="title" placeholder="例如：八年级 Unit 3 单词默写" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="workDate" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" class="wide-control" />
        </el-form-item>
        <el-form-item label="完整版份数">
          <el-input-number v-model="originalCopies" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="默写版份数">
          <el-input-number v-model="dictationCopies" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="打印机">
          <el-select v-model="printer" class="wide-control" placeholder="选择打印机">
            <el-option label="默认打印机" value="default" />
            <el-option label="家用打印机" value="home" />
            <el-option label="办公室打印机" value="office" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-button type="primary" size="large" :loading="parsing" @click="parseHomework">AI解析作业</el-button>
    </section>

    <section class="preview-area">
      <div class="preview-grid">
        <el-card shadow="always" class="preview-card">
          <template #header><strong>【预览】完整版（英语.docx）</strong></template>
          <el-input :model-value="originalPreview" class="preview-textarea" type="textarea" resize="none" readonly placeholder="点击左侧“AI解析作业”后生成完整中英对照预览" />
        </el-card>

        <el-card shadow="always" class="preview-card">
          <template #header><strong>【预览】默写版（仅中文）</strong></template>
          <el-input :model-value="dictationPreview" class="preview-textarea" type="textarea" resize="none" readonly placeholder="点击左侧“AI解析作业”后生成默写版预览" />
        </el-card>
      </div>

      <div class="divider" />

      <div class="actions">
        <el-button type="success" size="large" :disabled="!items.length" :loading="saving" @click="saveDocument">生成Word文档</el-button>
        <el-button size="large" :disabled="!documentInfo" @click="downloadDoc('original')">下载完整版</el-button>
        <el-button size="large" :disabled="!documentInfo" @click="downloadDoc('dictation')">下载默写版</el-button>
        <el-button type="primary" size="large" :disabled="!items.length" @click="printPreview('original')">打印完整版</el-button>
        <el-button type="warning" size="large" :disabled="!items.length" @click="printPreview('dictation')">打印默写版</el-button>
      </div>

      <el-alert
        v-if="documentInfo"
        class="result-alert"
        type="success"
        show-icon
        :closable="false"
        :title="`已入库：文档 #${documentInfo.document_id}，共 ${documentInfo.word_count} 个单词，可前往文档管理和单词检索查看。`"
      />
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createDocument, exportDictationDocument, exportOriginalDocument, parseText } from '@/api/client'

const today = new Date().toISOString().slice(0, 10)
const text = ref('apple 苹果\nbanana 香蕉\nbeautiful 美丽的')
const title = ref('粘贴文本')
const workDate = ref(today)
const originalCopies = ref(1)
const dictationCopies = ref(2)
const printer = ref('')
const items = ref([])
const parsing = ref(false)
const saving = ref(false)
const documentInfo = ref(null)

const normalizedTitle = computed(() => {
  const suffix = workDate.value ? `（${workDate.value}）` : ''
  return `${title.value || '粘贴文本'}${suffix}`
})

const originalPreview = computed(() => items.value.map((item) => `${item.word.padEnd(16, ' ')}${item.meaning}`).join('\n'))
const dictationPreview = computed(() => items.value.map((item) => `${'__________'.padEnd(16, ' ')}${item.meaning}`).join('\n'))

async function parseHomework() {
  if (!text.value.trim()) {
    ElMessage.warning('请先粘贴作业文本')
    return
  }
  parsing.value = true
  documentInfo.value = null
  try {
    const { data } = await parseText(text.value, normalizedTitle.value)
    items.value = data.data.items
    if (!items.value.length) {
      ElMessage.warning('没有识别到“英文 中文”格式的单词，请检查输入内容')
      return
    }
    ElMessage.success(`解析完成，共识别 ${items.value.length} 个单词`)
  } finally {
    parsing.value = false
  }
}

async function saveDocument() {
  if (!items.value.length) {
    await parseHomework()
    if (!items.value.length) return
  }
  saving.value = true
  try {
    const { data } = await createDocument(text.value, normalizedTitle.value)
    documentInfo.value = data.data
    ElMessage.success(`Word 文档生成并入库成功，单词数：${data.data.word_count}`)
  } finally {
    saving.value = false
  }
}

async function downloadDoc(type) {
  if (!documentInfo.value?.document_id) {
    ElMessage.warning('请先生成 Word 文档')
    return
  }
  const request = type === 'original' ? exportOriginalDocument : exportDictationDocument
  const { data } = await request(documentInfo.value.document_id)
  const url = URL.createObjectURL(data)
  const link = document.createElement('a')
  link.href = url
  link.download = `${normalizedTitle.value}-${type === 'original' ? '完整版' : '默写版'}.docx`
  link.click()
  URL.revokeObjectURL(url)
}

function escapeHtml(value) {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;')
}

function printPreview(type) {
  const content = type === 'original' ? originalPreview.value : dictationPreview.value
  const copies = type === 'original' ? originalCopies.value : dictationCopies.value
  if (!content) {
    ElMessage.warning('请先解析作业')
    return
  }
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    ElMessage.error('浏览器阻止了打印窗口，请允许弹窗后重试')
    return
  }
  printWindow.document.write(`
    <html>
      <head>
        <title>${type === 'original' ? '完整版' : '默写版'}打印</title>
        <style>body{font-family:Arial,"Microsoft YaHei",sans-serif;padding:32px;line-height:1.9;} pre{font-size:18px;white-space:pre-wrap;}</style>
      </head>
      <body>
        <h2>${normalizedTitle.value}</h2>
        <p>打印份数：${copies}${printer.value ? ` ｜ 打印机：${printer.value}` : ''}</p>
        <pre>${escapeHtml(content)}</pre>
      </body>
    </html>
  `)
  printWindow.document.close()
  printWindow.focus()
  printWindow.print()
}
</script>

<style scoped>
.workbench-page {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 28px;
  min-height: calc(100vh - 32px);
}

.input-panel {
  padding-right: 28px;
  border-right: 1px solid #e5e7eb;
}

.panel-title {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}

.source-textarea :deep(.el-textarea__inner) {
  min-height: 360px !important;
  font-size: 16px;
  line-height: 1.7;
}

.divider {
  margin: 24px 0;
  border-top: 1px solid #e5e7eb;
}

.setting-form {
  max-width: 320px;
}

.wide-control {
  width: 100%;
}

.preview-area {
  min-width: 0;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  gap: 24px;
}

.preview-card :deep(.el-card__header) {
  padding: 18px 24px;
  font-size: 18px;
}

.preview-textarea :deep(.el-textarea__inner) {
  min-height: 520px !important;
  padding: 18px;
  font-family: Consolas, Monaco, monospace;
  font-size: 16px;
  line-height: 1.8;
  background: #fff;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
}

.result-alert {
  margin-top: 20px;
}

@media (max-width: 1180px) {
  .workbench-page {
    grid-template-columns: 1fr;
  }

  .input-panel {
    padding-right: 0;
    border-right: 0;
  }
}
</style>
