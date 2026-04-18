# Functional Design Document

# Student Sentiment Analysis API

**Version:** 1.0.0
**Author:** Danyon Satyam
**Mentor/Client:** Pramit Dash
**Date:** April 2026
**Status:** In Development

---

## 1. Purpose

This document describes the functional design of the Student Sentiment
Analysis API — a production-grade REST API that enables universities to
collect student feedback at scale and automatically classify student
sentiment using machine learning.

The primary audience is Pramit Dash (technical mentor and client) and
any developer joining the project.

---

## 2. Problem Statement

Universities collect student feedback through surveys but lack automated
tools to analyse sentiment at scale. Manual analysis of hundreds of
feedback records is slow, inconsistent, and impossible to do in real time.

The Student Sentiment API solves this by:

- Accepting structured student feedback via a REST API
- Automatically classifying sentiment as Positive, Neutral, or Negative
  using a trained CatBoost ML model
- Providing aggregated analytics endpoints for university dashboards
- Identifying at-risk students who may need academic intervention

---

## 3. System Architecture

    Client (Browser / University App)
                                                 │
                                                 ▼ HTTP Request
┌───────────────────────┐
│   FastAPI Application                                                            │
│   (Uvicorn ASGI server)                                                        │
└──────────┬────────────┘
                                                 │
                  ┌──────┴──────┐
                  │                                                          │
                  ▼                                                          ▼
           Feedback                                          Analytics
           Endpoints                                        Endpoints
                                                │
                                                ▼
                              FeedbackRepository
                              (Repository Pattern)
                                                │
                                                ▼
                                SQLAlchemy ORM
                                                │
                                                ▼
                            PostgreSQL Database

---

## 4. Core Domain Objects

### StudentFeedback

The central entity. Represents one student's feedback submission.

| Field                 | Type       | Constraints | Description                     |
| --------------------- | ---------- | ----------- | ------------------------------- |
| id                    | Integer    | PK, auto    | Unique identifier               |
| roll_number           | String(20) | Not null    | Student roll number             |
| gender                | String(10) | Not null    | Male/Female/Other               |
| age                   | Integer    | 17-35       | Student age                     |
| study_hours_per_day   | Integer    | 1-24        | Daily study hours               |
| attendance_percentage | Integer    | 0-100       | Attendance %                    |
| active_backlogs       | Integer    | >= 0        | Number of backlogs              |
| academic_feedback     | String(20) | Not null    | Excellent/Good/Satisfactory/Bad |
| emotional_feedback    | String(20) | Not null    | Happy/Glad/Neutral/Sad/Angry    |
| sentiment_label       | String(20) | Not null    | Positive/Neutral/Negative       |
| created_at            | DateTime   | Not null    | Submission timestamp            |

### Feedback (CRUD)

| Method | Path                  | Description        | Status Code |
| ------ | --------------------- | ------------------ | ----------- |
| POST   | /api/v1/feedback      | Submit feedback    | 201         |
| GET    | /api/v1/feedback      | List all + summary | 200         |
| GET    | /api/v1/feedback/{id} | Get one record     | 200         |
| PATCH  | /api/v1/feedback/{id} | Update record      | 200         |
| DELETE | /api/v1/feedback/{id} | Delete record      | 204         |

### Analytics

| Method | Path                           | Description                      |
| ------ | ------------------------------ | -------------------------------- |
| GET    | /api/v1/analytics/summary      | Overall sentiment distribution   |
| GET    | /api/v1/analytics/by-sentiment | Filter by sentiment label        |
| GET    | /api/v1/analytics/trends       | Breakdown by gender and feedback |
| GET    | /api/v1/analytics/at-risk      | At-risk student identification   |

---

## 6. Sentiment Prediction Pipeline

Input: emotional_feedback + academic_feedback
                                                          │
                                                          ▼
                              SentimentMLService.predict()
                                                          │
                                                          ├── ML model available? ──YES──▶ CatBoost prediction
                                                          │                                                                                                       │
                                                          └── NO ──▶ Rule-based fallback                              │
                                                                                               (weighted scoring)                                │
                                                                                                                │                                                 │
                                                                                                                └─────┬─────┘
                                                                                                                                           ▼
                                                                                                             'Positive' / 'Neutral' / 'Negative'

---

## 7. At-Risk Student Criteria

A student is flagged as at-risk if they meet ANY of:

1. Sentiment label is Negative
2. Active backlogs >= 2
3. Attendance percentage < 60%

## 8. Non-Functional Requirements

| Requirement      | Target                                  |
| ---------------- | --------------------------------------- |
| Concurrent users | 100+ simultaneous                       |
| Response time    | < 200ms for CRUD, < 500ms for analytics |
| Test coverage    | > 80%                                   |
| CI pipeline      | Passes on every push                    |
| Deployment       | GCP Cloud Run                           |
