# Advanced Network Calculator & VLSM Wizard v2.0

A comprehensive network analysis and planning toolkit designed for network engineers, cybersecurity professionals, and students. This advanced tool provides VLSM calculations, network scanning, topology visualization, AI-powered troubleshooting, and educational resources in a single, intuitive interface.

## 🚀 Features

### 📊 Advanced VLSM & Subnetting
- **Dynamic Subnet Generation**: Create multiple subnets with custom host requirements
- **Utilization Analysis**: Real-time efficiency calculations with visual charts
- **Overlap Detection**: Automatic subnet conflict identification
- **Optimization Engine**: Intelligent subnet allocation for maximum efficiency
- **IPv6 Support**: Complete IPv6 subnetting capabilities

### 🔧 Network Tools Suite
- **CIDR Converter**: Bidirectional subnet mask and CIDR notation conversion
- **Supernetting Calculator**: Route summarization and aggregation
- **Bandwidth Calculator**: Multi-unit bandwidth conversions
- **Network Scanner**: Ping sweep and port scanning capabilities
- **Real-time Monitoring**: Live network performance analysis

### 🗺️ Topology Visualization
- **Interactive Network Maps**: Auto-generated topology diagrams
- **Graph-based Layout**: NetworkX integration for complex visualizations
- **CSV Import/Export**: Load existing network data
- **Customizable Views**: Multiple layout algorithms and styling options

### 🏷️ VLAN Management
- **VLAN Planning**: Comprehensive VLAN design and documentation
- **Configuration Generation**: Auto-generate switch configurations
- **Conflict Detection**: Identify VLAN and subnet conflicts
- **Multi-vendor Support**: Compatible configuration formats

### 🤖 AI-Powered Features
- **Intelligent Troubleshooting**: AI-assisted network problem resolution
- **ACL Generator**: Automated Access Control List creation
- **Model Integration**: Support for custom AI models (transformers, torch)
- **Context-Aware Solutions**: Network-specific recommendations

### 📚 Educational Components
- **Practice Mode**: Interactive subnetting exercises
- **Difficulty Scaling**: Beginner to expert level challenges
- **Multi-vendor CLI**: Comprehensive command reference (Cisco, Juniper, Huawei, HPE)
- **Progress Tracking**: Performance analytics and scoring

### 💾 Project Management
- **Save/Load Projects**: JSON-based project persistence
- **Export Documentation**: Generate comprehensive network documentation
- **CSV Integration**: Import/export network data
- **Dark Mode**: Professional UI with theme switching

## 🛠️ Installation

### Prerequisites
```bash
Python 3.8+ required
```

### Required Dependencies
```bash
pip install tkinter matplotlib networkx pandas numpy requests ipaddress
```

### Optional AI Features
```bash
pip install transformers torch
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/mrtimber425/VLSM-Wizard.git

# Navigate to directory
cd VLSM-Wizard

# Install dependencies
pip install -r requirements.txt

# Run application
python vlsm_wizard.py
```

## 📋 Usage Guide

### Basic VLSM Calculation
1. **Enter Base Network**: Input your network (e.g., `192.168.1.0/24`)
2. **Specify Requirements**: Add subnet names, host counts, and priorities
3. **Calculate**: Generate optimized subnet allocation
4. **Analyze**: Review efficiency metrics and utilization charts

### Network Scanning
1. **Ping Sweep**: Discover active hosts in network ranges
2. **Port Scanning**: Identify open ports on target systems
3. **Export Results**: Save scan data for further analysis

### VLAN Planning
1. **Design VLANs**: Create comprehensive VLAN schemes
2. **Generate Config**: Auto-produce switch configurations
3. **Validate Design**: Check for conflicts and overlaps

### AI Troubleshooting
1. **Load AI Model**: Import pre-trained or custom models
2. **Describe Issue**: Input network problems in natural language
3. **Get Solutions**: Receive AI-generated troubleshooting steps

## 🏗️ Architecture

### Core Components
- **GUI Framework**: tkinter with professional styling
- **Calculation Engine**: Advanced algorithms for subnet optimization
- **Visualization Engine**: matplotlib and NetworkX integration
- **AI Integration**: Transformers library for natural language processing
- **Data Management**: JSON/CSV for persistence and import/export

### Technical Features
- **Multi-threading**: Non-blocking network operations
- **Error Handling**: Comprehensive exception management
- **Extensible Design**: Modular architecture for easy enhancement
- **Cross-platform**: Compatible with Windows, Linux, and macOS

## 🎯 Use Cases

### Network Engineering
- **Subnet Planning**: Design efficient IP addressing schemes
- **Capacity Planning**: Analyze network utilization and growth
- **Documentation**: Generate comprehensive network documentation
- **Troubleshooting**: Systematic problem diagnosis and resolution

### Cybersecurity
- **Network Reconnaissance**: Automated discovery and scanning
- **Vulnerability Assessment**: Identify potential security gaps
- **Infrastructure Mapping**: Visualize network topology for threat modeling
- **Security Planning**: Design secure network segmentation

### Education & Training
- **Hands-on Learning**: Interactive subnetting practice
- **Skill Assessment**: Track learning progress and competency
- **Reference Material**: Multi-vendor CLI command database
- **Certification Prep**: Practice scenarios for networking certifications

## 🔧 Advanced Configuration

### Custom AI Models
```python
# Load custom troubleshooting model
model_path = "/path/to/custom/model"
app.load_ai_model(model_path)
```

### Network Templates
```python
# Import network topology from CSV
topology_data = "network_topology.csv"
app.load_topology_csv(topology_data)
```

### Automation Scripts
```python
# Batch subnet calculations
subnets = [
    {"name": "Users", "hosts": 100, "priority": "High"},
    {"name": "Servers", "hosts": 50, "priority": "High"},
    {"name": "Guest", "hosts": 25, "priority": "Low"}
]
app.calculate_batch_vlsm(subnets)
```

## 🤝 Contributing

We welcome contributions! Areas for enhancement:
- Additional vendor CLI support
- Advanced AI model integration
- Enhanced visualization options
- Network simulation capabilities
- Mobile/web interface development

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Author

**I Kadek Ogika Indrabramasta Wibawa**
- LinkedIn: [linkedin.com/in/i-wibawa](https://linkedin.com/in/i-wibawa)
- GitHub: [github.com/mrtimber425](https://github.com/mrtimber425)

## 🏆 Acknowledgments

- Network engineering community for feature requests and feedback
- Open source libraries: matplotlib, NetworkX, tkinter
- AI/ML community for transformers and PyTorch integration
- Educational institutions for testing and validation

---

*Built with ❤️ for the network engineering and cybersecurity community*
