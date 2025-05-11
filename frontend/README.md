# Job Tinder

[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.2-646CFF.svg)](https://vitejs.dev/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-5.25-0170FE.svg)](https://ant.design/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A modern, AI-powered job search and analysis platform built with React, TypeScript, and Ant Design. **JobTinder** helps users find their ideal career opportunities through intelligent matching and detailed job analysis.

## Features

- **Job Search & Discovery**:
  - Seamless searching job through multiple sources
  - AI-powered job matching based on user skills and preferences
  - Advanced search with multiple filters (job level, job title)
  - Semantic search queries

- **Job Analysis**
  - Comprehensive job analysis with match scoring
  - Strengths and weaknesses assessment based on user profile
  - Personalized feedback on skill gaps

- **AI Assistant**
  - Interactive chatbot for career advice and guidance
  - Personalized responses with rich markdown formatting

- **User Authentication & Profile**
  - Secure login and registration system
  - CV upload and automated skills extraction
  - Profile customization and management
  - Saved jobs and favorites

- **Modern UI Experience**:
  - Responsive design for all devices
  - Animated components with Framer Motion
  - Rich markdown rendering

## Tech Stack

- **Core**:
  - React 19
  - TypeScript 5.7
  - Vite 6.2
- **UI Framework**:
  - Ant Design 5.25
  - Framer Motion 12.9 (animations)
- **State Management & Data Fetching**:
  - Zustand 5.0
  - TanStack React Query 5.75
  - React Hook Form 7.54
- **Routing**:
  - React Router DOM 7.5
- **Axios**
- **ESLint + Prettier**

## Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)
- yarn or npm

### Installation

1. Clone the repository:


2. Install dependencies:
```bash
yarn install
```

3. Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

4. Update the `.env` file with your API endpoint if needed:
```
VITE_API_BASE_URL=http://localhost:8080/api/v1
```

### Development

To start the development server:

```bash
yarn dev
```

The application will be available at `http://localhost:5173`\

Add new packages:
```bash
# Add a production dependency
yarn add package-name

# Add a development dependency
yarn add -D package-name

# Add specific version
yarn add package-name@1.2.3
```

Working with Git
```bash
# Create a new feature branch
git checkout -b feature/feature-name

# Create a new bugfix branch
git checkout -b bugfix/issue-description

# Commit changes with conventional commits
git commit -m "feat: add new job filter component"
git commit -m "fix: infinite loading in job search page"
git commit -m "docs: update environment variable documentation"
```

### Building for Production

To create a production build:

```bash
yarn build
```

To preview the production build:

```bash
yarn preview
```

### Linting

To run the linter:

```bash
yarn lint
```

## Project Structure

```
src/
├── assets/               # Static assets (images, SVGs)
├── components/           # Shared and Reusable UI components
│   ├── ai-button/        # Custom AI-styled buttons
│   ├── custom-markdown/  # Markdown renderer with syntax highlighting
│   ├── fullscreen-loader/# Loading screen overlay
│   ├── magic-ui/         # Animation components (typewriter, flip words)
│   ├── navbar/           # Navigation header
├── contexts/             # React context providers
│   └── auth/             # Authentication context
├── hooks/                # Custom React hooks
├── lib/                  # Utilities, configurations
│   ├── clients/          # Common client configuration (Axios, React Query)
│   ├── constants/        # App constants and enumerations
│   ├── helpers/          # Helper functions
│   └── types/            # TypeScript interfaces and types
├── pages/                # Application pages by feature
│   ├── ai-assistant/     # AI chatbot interface
│   ├── auth/             # Authentication screens
│   ├── job-analysis/     # Job analysis interface
│   ├── job-finder/       # Job search and listing
│   └── interrupts/       # Error pages (404, etc.)
├── routes/               # Routing configuration
├── services/             # API services by domain
└── App.tsx               # Root application component
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_BASE_URL | Backend API URL | http://localhost:8080/api/v1 |

## License

This project is licensed under the MIT License.
