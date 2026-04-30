<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

// 全局错误处理
onMounted(() => {
  console.log('智能手写笔记转录系统已启动')
})
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
  background: #f5f7fa;
}

/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  font-size: 14px;
}

/* 链接样式 */
a {
  text-decoration: none;
  color: inherit;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8b0c0;
}
</style>
