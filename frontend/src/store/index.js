import { configureStore } from '@reduxjs/toolkit'
import chessReducer from './chessSlice'
import themeReducer from './themeSlice'

export const store = configureStore({
  reducer: {
    chess: chessReducer,
    theme: themeReducer
  },
})