import { createStore } from 'vuex'

export default createStore({
  state: {
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    menus: []
  },
  
  mutations: {
    setToken(state, token) {
      const tokenWithBearer = token.startsWith('Bearer ') ? token : `Bearer ${token}`
      state.token = tokenWithBearer
      localStorage.setItem('token', tokenWithBearer)
    },
    setUser(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    clearToken(state) {
      state.token = ''
      state.user = null
      state.menus = []
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    setMenus(state, menus) {
      state.menus = menus
    }
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    authToken: state => state.token,
    currentUser: state => state.user
  }
}) 