import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebar: {
      opened: localStorage.getItem('sidebarStatus') !== 'closed',
      withoutAnimation: false
    },
    device: 'desktop',
    size: localStorage.getItem('size') || 'default'
  }),
  
  actions: {
    toggleSidebar() {
      this.sidebar.opened = !this.sidebar.opened
      this.sidebar.withoutAnimation = false
      if (this.sidebar.opened) {
        localStorage.setItem('sidebarStatus', 'opened')
      } else {
        localStorage.setItem('sidebarStatus', 'closed')
      }
    },
    
    closeSidebar(withoutAnimation) {
      this.sidebar.opened = false
      this.sidebar.withoutAnimation = withoutAnimation
      localStorage.setItem('sidebarStatus', 'closed')
    },
    
    toggleDevice(device) {
      this.device = device
    },
    
    setSize(size) {
      this.size = size
      localStorage.setItem('size', size)
    }
  }
})
