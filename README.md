# Seraface - AI Skincare App

**Seraface** is an elegant, AI-powered mobile application that analyzes facial skin, identifies conditions, and recommends personalized skincare routines and products — all tailored to the user's needs and budget.

## ✨ Features

- 📸 **Facial Skin Scan** using AI and computer vision
- 🧠 **Smart Analysis** of skin type, concerns, and conditions
- 🧴 **Personalized Skincare Routines** powered by AI
- 🛒 **Product Recommendations** based on ingredients, past usage, and budget
- 📊 **Progress Tracking** to monitor skin improvements over time
- 💡 **User-Centered Design** with a clean, modern mobile interface

## ⚙️ Tech Stack

- **Frontend**: ReactJS (Vite) + Tailwind CSS
- **Mobile**: CapacitorJS
- **Backend**: FastAPI (planned)
- **AI & CV**: Python-based models (planned for skin analysis)

## 🚀 Getting Started

### Prerequisites

- Node.js v18+
- Capacitor CLI

### Install and Run

```bash
# Clone the repo
https://github.com/dandee77/Seraface-AI.git

cd Seraface-AI

# Install dependencies
npm install

# Run the app in development
npm run dev
```

### Build and Deploy to Mobile

```bash
# Build for production
npm run build

# Copy build to Capacitor
npx cap copy

# Open in Android Studio or Xcode
npx cap open android
# or
npx cap open ios
```

## 📁 Project Structure

```
seraface-ai-skincare/
├── api/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── App.jsx
├── capacitor.config.ts
├── index.html
├── package.json
└── vite.config.js
```

## 📌 Roadmap

- [x] Set up React + Vite + Capacitor
- [ ] Integrate face scanning with AI skin detection
- [ ] Build budget-based recommendation engine
- [ ] Connect to backend (FastAPI)
- [ ] Add user account system
- [ ] Polish UI/UX and animations

## 🧑‍💻 Authors

**Dandee Galang** – [@dandee77](https://github.com/dandee77) <br/>
**Aaron Ersando** - [@aaronersando](https://github.com/aaronersando)

## 📄 License

This project is licensed under the MIT License.

---

> "Let your skin glow with insight." – _Seraface_
