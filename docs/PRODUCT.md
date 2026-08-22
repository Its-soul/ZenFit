# Product & Design Specification

ZenFit is an adaptive daily fitness coach. Its primary goal is not just data collection, but acting as a behavior system designed to help users maintain momentum when motivation drops. 

## 1. Product Strategy

### Product Promise
ZenFit is your adaptive daily fitness coach. It reads the state of your day, your recent behavior, and your recovery, then gives you one clear next step.

### Core Product Loop
1. **Identify**: User opens Today; ZenFit identifies their daily state.
2. **Recommend**: ZenFit gives one recommended action.
3. **Act**: User completes, adjusts, or skips the action.
4. **Adapt**: ZenFit responds emotionally and adapts the plan.
5. **Momentum**: User sees momentum preserved.

## 2. Features & Capabilities

### Data & Memory
- **Semantic Memory**: Durable preferences and repeated behavior are stored per user and reranked before use to contextualize recommendations.
- **Predictive Analytics**: The system analyzes adherence, readiness, and recommendation acceptance.

### Nutrition & Meal Scanning
- **Meal Analysis**: Optional local segmentation and classification to provide conservative portions and USDA nutrition.
- **User Trust**: Explicit uncertainty is surfaced, and manual confirmation is always required.
- **Capability States**:
  - `Ready`: Full recognition available.
  - `Partial`: Incomplete recognition, requires heavier user input.
  - `Fallback`: Manual entry required (the baseline safe UX).
  - `Unavailable`: Explicitly informing the user when a service is offline.

### Exercise Analysis
- **Pose Tracking**: Normalized client-derived landmarks produce rep counts, range-of-motion observations, and tempo timestamps.
- **Privacy First**: Heavy image/video analysis happens securely or on-device where possible.

## 3. UX Design Principles

- **Clarity over Complexity**: The UI never describes unavailable recognition as ready. Honest fallback states (e.g., manual meal entry) are treated as first-class citizens.
- **Action-Oriented**: The dashboard focuses on the next immediate action rather than overwhelming the user with raw data.
- **Transparency**: Recommendation UI should show triggering factors and whether ranking came from rules or a trained model. Safety messages replace training advice when a transparent red flag fires.
