# Final Exam - When2Meet Clone

[![Live Site](https://img.shields.io/badge/Live%20App-Click%20Here-brightgreen?style=for-the-badge)](https://flask-app-429701463375.us-central1.run.app/login)

# When2Meet Clone

A real-time group scheduling web application inspired by [When2Meet](https://www.when2meet.com). This project was developed as the Final Exam for the Web Application Development course and is designed to demonstrate mastery of key concepts in modern web development, including reactive front-end design, secure and data-driven back-end systems, asynchronous communication, and real-time synchronization using WebSockets.

---

## Purpose

This application serves as a clone of When2Meet, allowing users to collaboratively mark their availability across multiple days and times to find the optimal meeting time for a group. The exam emphasizes the practical implementation of:

- Reactive front-end user interfaces
- Data-driven and session-based back-end systems
- Secure login and user authentication
- Real-time updates and WebSocket-based synchronization

---

## Features

### 1. User Authentication
- Secure sign-up and login system using email and password
- Passwords are stored securely using encryption
- Session-based access control ensures only logged-in users can view and edit event data

### 2. Event Management
- Users can create new scheduling events by providing:
  - Event name
  - Date range
  - Daily time range
  - List of invited users by email
- Users can join events they were invited to and view full metadata

### 3. Interactive Availability Grid
- Grid dynamically displays 30-minute time slots across the event's date range
- Three selectable availability modes: `Available`, `Maybe`, and `Unavailable`
- Users can click or drag to mark their availability
- Visual indicators and colors reflect selected modes in real-time
- All availability data is stored and persisted in the backend

### 4. Heatmap Visualization
- Grid displays collective group availability
- Color intensity increases as more users select `Available` for a given slot
- Distinct hues differentiate between `Maybe` and `Unavailable`
- Automatically updates in real-time for all connected users

### 5. Best Time to Meet
- Algorithm identifies the best 30-minute time slot based on:
  1. Maximum number of users available
  2. Minimum number of users unavailable
  3. Earliest time slot in case of tie
- Displayed prominently on the event page

### 6. Real-Time Synchronization (WebSockets)
- All changes to availability, heatmap, and "Best Time" are reflected instantly across all users on the same Event Page
- Uses WebSocket technology for real-time communication
- Ensures a live, collaborative experience without page refreshes or polling

---

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python / Flask
- **Database**: MySQL
- **Authentication**: Sessions and hashed passwords (bcrypt)
- **WebSockets**: Socket.io or native WebSocket API for real-time sync
- **Deployment**: Docker-compatible; stand-alone app

---

## Access Control

- All event pages are private and accessible **only** to invited users
- Non-invitees are denied access with appropriate messaging
- Session-based routing prevents unauthorized access to protected views

---

## Exam Notes

This project was submitted as a **stand-alone application** for the Final Exam and is **not integrated with prior homework assignments**. While some components may have been reused, all exam-specific logic and UI are implemented independently to meet the rubric-based grading criteria.

---

## 📄 License

This project is for academic purposes only and is not affiliated with or endorsed by When2Meet.



## Run Locally

```bash
docker-compose up --build
