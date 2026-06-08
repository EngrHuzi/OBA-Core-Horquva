const express = require('express')
const cors = require('cors')
require('dotenv').config()

const app = express()

app.use(cors())
app.use(express.json())

app.use('/api/agents', require('./routes/agents'))
app.use('/api/ownership', require('./routes/ownership'))
app.use('/api/dependencies', require('./routes/dependencies'))
app.use('/api/risks', require('./routes/risks'))
app.use('/api/dashboard', require('./routes/dashboard'))

const PORT = process.env.PORT || 3000

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
})
