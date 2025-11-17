# Online Marketplace for Handcrafted Goods

**Project ID:** P30  
**Course:** UE23CS341A  
**Academic Year:** 2025  
**Semester:** 5th Sem  
**Campus:** EC  
**Branch:** CSE  
**Section:** C  
**Team:** Woodman's World

## 📋 Project Description

A storefront that allows artisans to list handmade items, buyers to place orders, and view simple sales and inventory reports. The project uses a relational database for product/catalog management, shopping-cart workflows, and PDF invoice generation.

This repository contains the source code and documentation for the Online Marketplace for Handcrafted Goods project, developed as part of the UE23CS341A course at PES University.

## 🧑‍💻 Development Team (Woodman's World)

- [@GMen0n](https://github.com/GMen0n) - Scrum Master
- [@C-VISHWA](https://github.com/C-VISHWA) - Developer Team
- [@thedivsharma](https://github.com/thedivsharma) - Developer Team
- [@dhruvm-04](https://github.com/dhruvm-04) - Developer Team

## 👨‍🏫 Teaching Assistant

- [@nikitha-0704](https://github.com/nikitha-0704)
- [@samwilson129](https://github.com/samwilson129)
- [@harshamogra](https://github.com/harshamogra)

## 👨‍⚖️ Faculty Supervisor

- [@sudeeparoydey](https://github.com/sudeeparoydey)


## 🚀 Getting Started

### Prerequisites
- Hardware: Machine capable of running Docker or Python+Django locally (4 GB+ RAM).
- Software:
   - Python 3.11 (matches CI).
   - Django (version from requirements.txt).
   - Modern browser (Chrome/Firefox/Edge).
 
### Installation
1. Clone the repository
   ```bash
   git clone https://github.com/pestechnology/PESU_EC_CSE_C_P30_Online_Marketplace_for_Handcrafted_Goods_Woodman-s-World.git
   cd PESU_EC_CSE_C_P30_Online_Marketplace_for_Handcrafted_Goods_Woodman-s-World
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r src/requirements.txt
   ```

3. Run the application
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # optional, for admin access
   python manage.py runserver
   ```

## 📁 Project Structure

```
PESU_EC_CSE_C_P30_Online_Marketplace_for_Handcrafted_Goods_Woodman-s-World/
├── src/                 # Source code
├── docs/               # Documentation
├── tests/              # Test files
├── .github/            # GitHub workflows and templates
├── README.md          # This file
└── ...
```

## 🛠️ Development Guidelines

### Branching Strategy
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches

### Commit Messages
Follow conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test-related changes

### Code Review Process
1. Create feature branch from `develop`
2. Make changes and commit
3. Create Pull Request to `develop`
4. Request review from team members
5. Merge after approval

## 📚 Documentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)

## 🧪 Testing

```bash
python manage.py test --noinput -v 2
```

## 📄 License

This project is developed for educational purposes as part of the PES University UE23CS341A curriculum.

---

**Course:** UE23CS341A  
**Institution:** PES University  
**Academic Year:** 2025  
**Semester:** 5th Sem
