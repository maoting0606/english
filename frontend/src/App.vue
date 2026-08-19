<template><el-container><el-aside width="220px"><h2>单词默写系统</h2><el-menu router :default-active="$route.path"><el-menu-item v-for="item in nav" :key="item.path" :index="item.path">{{ item.title }}</el-menu-item></el-menu></el-aside><el-main><router-view /></el-main></el-container></template>
<script setup>
const nav=[{path:'/workbench',title:'单词工作台'},{path:'/file',title:'文档管理'},{path:'/search',title:'单词检索'},{path:'/ocr-check',title:'拍照默写批改'},{path:'/audio-score',title:'发音评测'},{path:'/error-book',title:'错题本'},{path:'/setting',title:'系统设置'}]
</script>
<style>body{margin:0;background:#f6f7fb}.el-aside{min-height:100vh;background:#fff;border-right:1px solid #eee;padding:16px}h2{font-size:18px}</style>
