# 🌐 Nexus Social Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![Real-time](https://img.shields.io/badge/Real--time-Socket.IO-orange.svg)

A modern, real-time social media platform built with Flask featuring instant messaging, push notifications, and comprehensive admin controls.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api) • [Deployment](#-deployment)

</div>

## 🚀 Features

### 👥 Social Features
- **User Authentication** - Secure registration and login system
- **Profile Management** - Customizable user profiles with bios and avatars
- **Post System** - Create, edit, and delete posts with rich content
- **Like & Comment** - Interactive engagement with posts
- **Real-time Chat** - Instant messaging with Socket.IO
- **User Discovery** - Find and connect with other users

### 🛡️ Admin Features
- **Admin Dashboard** - Comprehensive overview and statistics
- **User Management** - View, warn, ban, and manage users
- **Content Moderation** - Delete inappropriate posts and comments
- **Report System** - Handle user reports efficiently
- **Analytics** - Platform usage insights

### 🔔 Notification System
- **Real-time Alerts** - Instant notifications for likes, comments, messages
- **Push Notifications** - Browser push notifications even when app is closed
- **In-app Bell** - Notification center with dropdown interface
- **Multi-channel** - Both in-app and external notifications

### 💻 Technical Features
- **Responsive Design** - Works on desktop and mobile devices
- **Real-time Updates** - Live feeds without page refresh
- **RESTful API** - Clean API endpoints for extensibility
- **Database ORM** - SQLAlchemy for robust database operations
- **Security** - Password hashing, session management, CSRF protection

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask, Python |
| **Database** | SQLite, SQLAlchemy ORM |
| **Real-time** | Flask-SocketIO |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Notifications** | Service Workers, Push API |
| **Authentication** | Flask-Login, Werkzeug Security |
| **Templates** | Jinja2 |

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnkravin9-design/nexus-python.git
   cd nexus-python
