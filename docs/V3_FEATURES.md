# EFT Helper v3.0 — Dynamic Build System

## Overview

Version 3.0 transforms EFT Helper from a static build catalog to an intelligent, adaptive build generation system. The bot now generates builds dynamically based on user constraints (budget, trader loyalty, Flea Market access) and evaluates each build with a quality tier system.

## 🎯 Key Features

### 1. **Dynamic Build Generation** 🎲
- **On-the-fly generation**: No more pre-loaded static builds (except quest builds)
- **Smart constraints**: Budget, trader loyalty levels, Flea Market filtering
- **Real-time compatibility**: Uses tarkov.dev API to ensure module compatibility
- **Quality evaluation**: Each build receives a tier rating (S/A/B/C/D)

### 2. **Module Compatibility System** 🔧
- **Slot validation**: Checks if modules fit weapon slots
- **Automatic filtering**: Only shows compatible modules
- **Required slots**: Ensures all mandatory slots are filled

### 3. **Tier Evaluation System** 🏆
- **Quality ratings**: S-Tier (best) to D-Tier (weak)
- **Multi-factor scoring**:
  - Ergonomics and recoil balance
  - Cost efficiency
  - Completeness of build
  - Key modules (sight, stock, grip)
  - Improvement over base weapon
- **Improvement suggestions**: Provides tips for lower-tier builds

### 4. **User Build System** 💾
- **Save builds**: Save generated builds with custom names
- **Build collection**: View all your saved builds
- **Public/Private**: Share builds with community or keep private
- **Statistics tracking**: Ergonomics, recoil, cost, tier rating

### 5. **Community Builds** 👥
- **Browse public builds**: See what other players created
- **Like system**: Show appreciation for good builds
- **Copy builds**: Clone community builds to your collection
- **Sorting**: By popularity (likes) and recency

## 📊 Technical Architecture

### New Database Tables

#### `user_builds`
```sql
CREATE TABLE user_builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weapon_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    modules TEXT NOT NULL,           -- JSON array of module IDs
    total_cost INTEGER NOT NULL,
    tier_rating TEXT NOT NULL,       -- S/A/B/C/D
    ergonomics INTEGER,
    recoil_vertical INTEGER,
    recoil_horizontal INTEGER,
    is_public BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (weapon_id) REFERENCES weapons (id)
);
```

### New Services

#### `CompatibilityChecker`
- Validates module-slot compatibility
- Uses tarkov.dev weapon slot data
- Filters modules by allowed items/categories
- Handles exclusion lists

#### `TierEvaluator`
- Scores builds based on multiple factors
- Assigns tier ratings (S/A/B/C/D)
- Provides improvement suggestions
- Language-aware descriptions

#### `BuildGenerator`
- Generates random builds within constraints
- Selects weapons within budget
- Fills required slots first
- Optimizes optional slots
- Calculates final statistics

### New Handlers

#### `dynamic_builds.py`
- `/dynamic_random_build` - Start generation flow
- Budget input and validation
- Build generation and display
- Save/regenerate options

#### `community_builds.py`
- `/community_builds` - View public builds
- `/my_builds` - View user's own builds
- Like, copy, share functionality
- Public/private toggle
- Build deletion

## 🎮 User Flow

### Dynamic Build Generation

1. User clicks **🎲 Динамическая сборка**
2. Bot asks for budget (e.g., 150000 ₽)
3. Bot generates build considering:
   - Budget constraints
   - User's trader loyalty levels
   - Module compatibility
   - Slot requirements
4. Bot displays:
   - Weapon name
   - Tier rating and description
   - Budget spent/remaining
   - Stats (ergonomics, recoil)
   - Module list
   - Availability sources
5. User can:
   - **💾 Save** - Enter name and save to collection
   - **🔄 Regenerate** - Generate new build with same budget
   - **◀️ Back** - Cancel

### Community Builds

1. User clicks **👥 Сборки сообщества**
2. Bot shows list of public builds sorted by likes
3. User selects a build
4. Bot displays full build details
5. User can:
   - **👍 Like** - Show appreciation
   - **📋 Copy** - Clone to own collection
   - **◀️ Back** - Return to list

### My Builds

1. User clicks **💾 Мои сборки**
2. Bot shows user's saved builds
3. User selects a build
4. Bot displays build details with management options
5. User can:
   - **🌐 Publish / 🔒 Hide** - Toggle public/private
   - **🗑 Delete** - Remove build (with confirmation)
   - **◀️ Back** - Return to list

## 📈 Tier Rating System

### Scoring Factors

| Factor | Max Points | Description |
|--------|-----------|-------------|
| Completeness | 20 | All required slots filled |
| Key Modules | 15 | Sight, stock, grip present |
| Ergonomics | 30 | Based on final ergo value |
| Recoil Control | 30 | Based on final recoil |
| Cost Efficiency | 5 | Cost per stat point |
| Improvement | Bonus | Better than base weapon |

### Tier Thresholds

- **S-Tier**: 85%+ score - Excellent, superior balance
- **A-Tier**: 70-84% - Very good, great performance
- **B-Tier**: 50-69% - Good, acceptable stats
- **C-Tier**: 30-49% - Average, room for improvement
- **D-Tier**: <30% - Weak, needs significant improvements

### Thresholds Reference

**Ergonomics:**
- Excellent: 50+
- Good: 35-49
- Average: 20-34
- Poor: <20

**Recoil (Vertical):**
- Excellent: ≤40
- Good: 41-60
- Average: 61-80
- Poor: >80

## 🔄 Migration from v2.x

Run the migration script:
```bash
python scripts/migrate_to_v3.py
```

This will:
1. Create backup of existing database
2. Create `user_builds` table
3. Add new columns to `builds` table
4. Preserve existing data

## 🚫 What's Removed

- ❌ Static random builds from database (kept for quests only)
- ❌ `planner_link` field (no longer used)
- ❌ Pre-populated build table (except quest builds)

## 🔮 Future Enhancements (Stage 2)

- **AI-Assisted Generation**: Integration with local AI (Ollama)
- **Advanced Filters**: Weapon type, caliber, play style
- **Build Templates**: Save configuration presets
- **Build Comparison**: Side-by-side comparison
- **Price History**: Track module prices over time
- **Build Analytics**: Most popular modules, average costs

## 📝 API Integration

All data sourced from **tarkov.dev GraphQL API**:
- Weapon data with slots
- Module compatibility
- Market prices
- Trader availability

## 🧪 Testing Checklist

- [ ] Dynamic build generation with various budgets
- [ ] Budget constraint enforcement
- [ ] Trader loyalty filtering
- [ ] Module compatibility validation
- [ ] Tier calculation accuracy
- [ ] Build save/load functionality
- [ ] Community build sharing
- [ ] Like/copy functionality
- [ ] Public/private toggle
- [ ] Build deletion
- [ ] Localization (RU/EN)
- [ ] Error handling

## 📚 Code Structure

```
services/
├── compatibility_checker.py  # Module slot validation
├── tier_evaluator.py        # Build quality rating
└── build_generator.py        # Dynamic build generation

handlers/
├── dynamic_builds.py         # Build generation flow
└── community_builds.py       # Community & user builds

database/
├── models.py                 # UserBuild model
└── db.py                     # user_builds CRUD operations
```

## 🎨 UI/UX Improvements

- **Better main menu**: Reorganized with v3.0 features first
- **Inline keyboards**: Rich interaction with buttons
- **Progress indicators**: Loading messages during generation
- **Tier emojis**: Visual tier representation
- **Formatted stats**: Clear presentation of build info

## 🌍 Localization

All v3.0 features fully localized:
- Russian (ru) - Primary
- English (en) - Secondary

New text keys: ~50+ entries

## ⚡ Performance

- **Caching**: Weapon slots cached after first fetch
- **Batch queries**: Module data fetched in bulk
- **Async operations**: Non-blocking API calls
- **Memory efficiency**: Temporary build data cleaned up

## 🐛 Known Limitations

1. **Module stats**: Some module properties may not be available from API
2. **Stat calculation**: Simplified calculation (real game uses complex formulas)
3. **Weapon mapping**: tarkov.dev IDs need mapping to internal DB IDs
4. **Rate limiting**: No API rate limiting implemented yet

## 📖 User Documentation

See [USER_GUIDE_V3.md](USER_GUIDE_V3.md) for end-user documentation.
