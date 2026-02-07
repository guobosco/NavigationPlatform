import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import { viteSingleFile } from "vite-plugin-singlefile"

// https://vitejs.dev/config/
export default defineConfig({
  base: './', // 使用相对路径，支持本地文件系统直接打开
  plugins: [
    vue(),
    UnoCSS(),
    viteSingleFile(), // 将所有资源内联到 index.html，解决 file:// 协议下的跨域和加载问题
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/token': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
