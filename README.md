# Ecosystem Simulation Project

![Streamlit Interface Demo](demo.gif)

## 📋 Project Description

This Python-based simulation models the movement, hunting, and reproduction dynamics of creatures within a 500x500-unit virtual ecosystem. Designed to analyze population changes through realistic interactions.

## 🌟 Core Features

- **Dynamic Movement System**  
  Random positional changes with species-specific movement ranges.
- **Hierarchical Hunting Mechanism**  
  Predators detect and hunt prey within defined distances.
- **Gender-Based Reproduction**  
  New individuals spawn when opposite genders of the same species approach.
- **Real-Time Visualization**  
  Track live creature locations and population statistics.

## 🐾 Creature Types & Abilities

| Species | Movement | Hunting | Prey       |
| ------- | -------- | ------- | ---------- |
| Sheep   | 2 units  | None    | -          |
| Wolf    | 3 units  | 4 units | Sheep      |
| Cow     | 1 unit   | None    | -          |
| Chicken | 1 unit   | None    | -          |
| Rooster | 1 unit   | None    | -          |
| Lion    | 4 units  | 5 units | Sheep, Cow |
| Hunter  | 3 units  | 8 units | Wolf, Lion |

## 📊 Data Structure

Each creature's data is stored in CSV format with:

- **ID**: Unique identifier
- **Species**: 7 distinct creature types
- **Gender**: Male/Female (except Chicken/Rooster)
- **Location**: [X,Y] coordinates (0-499 range)
- **Movement/Hunting Range**: Species-specific parameters
- **Prey List**: Huntable species

## 🖥️ Interface Features

- **Live Map**: 2D visualization with species-specific colors/icons
- **Statistics Dashboard**: Population distribution and gender ratios
- **Simulation Controls**:
  - Step count configuration (10-1000 steps)
  - Speed adjustment (0.1x-2x)
  - Real-time creature management
  - Step-by-step progression

## ⚙️ Technical Details

**Technologies Used**:

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- NumPy

**File Structure**:

```
├── living_class.py
├── main.py
├── creatures_list.csv
└── requirements.txt
```

## 🛠️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/username/ecosystem-simulation.git
   cd ecosystem-simulation
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the simulation:
   ```bash
   streamlit run main.py
   ```

**requirements.txt**:

```
streamlit==1.22.0
pandas==2.0.3
numpy==1.24.3
plotly==5.15.0
matplotlib==3.7.2
```

## 📌 Key Notes

- Chickens are exclusively female, roosters exclusively male
- Hunters operate independently of other species
- Final population report generated after every 1000 steps
- Coordinate wrapping ensures creatures stay within bounds
- All data persists in CSV format between sessions
