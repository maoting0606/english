import { createRouter, createWebHistory } from 'vue-router'
const routes = [
  { path: '/', redirect: '/workbench' },
  { path: '/workbench', name: 'Workbench', component: () => import('@/views/Workbench/index.vue'), meta: { title: '单词工作台', icon: 'document' } },
  { path: '/file', name: 'FileManage', component: () => import('@/views/FileManage/index.vue'), meta: { title: '文档管理', icon: 'folder' } },
  { path: '/file/preview/:docId', name: 'DocPreview', component: () => import('@/views/FileManage/Preview.vue'), meta: { title: '文档在线预览', hidden: true } },
  { path: '/search', name: 'WordSearch', component: () => import('@/views/Search/index.vue'), meta: { title: '单词检索', icon: 'search' } },
  { path: '/ocr-check', name: 'OcrCheck', component: () => import('@/views/Multimodal/OcrCheck.vue'), meta: { title: '拍照默写批改', icon: 'camera' } },
  { path: '/audio-score', name: 'AudioScore', component: () => import('@/views/Multimodal/AudioScore.vue'), meta: { title: '发音评测', icon: 'microphone' } },
  { path: '/error-book', name: 'ErrorBook', component: () => import('@/views/ErrorBook/index.vue'), meta: { title: '错题本', icon: 'list' } },
  { path: '/setting', name: 'Setting', component: () => import('@/views/Setting/index.vue'), meta: { title: '系统设置', icon: 'setting' } },
  { path: '/:pathMatch(.*)*', redirect: '/workbench' }
]
export default createRouter({ history: createWebHistory(), routes })
