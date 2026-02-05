# Credits and Attribution

## Data & Trust Alliance

This project uses the **Data Provenance Standards v1.0.0** developed by the [Data & Trust Alliance](https://www.dtaalliance.org/).

### Standards Development Team

The DTA provenance standards were co-developed by **19 organizations** including:

- AARP
- IBM
- Mastercard
- Deloitte
- Nike
- Pfizer
- Walmart
- CVS Health
- Nielsen
- Fidelity Investments
- SAP
- And others

The standards were developed through **150+ sessions** with **50+ organizations** testing and validating the framework.

### Official Resources

- **Specification**: [DTA Provenance Standards](https://github.com/Data-and-Trust-Alliance/DPS)
- **JSON Schema**: [Metadata Schema](https://github.com/Data-and-Trust-Alliance/json-metadata)
- **Website**: [DTAAlliance.org](https://www.dtaalliance.org/)

### Our Use of DTA Standards

This project:
- ✅ Implements the official DTA v1.0.0 specification
- ✅ Provides production-quality implementations
- ✅ Adds educational examples and documentation
- ✅ Compares implementation approaches (Git vs. Blockchain)

We are grateful to the Data & Trust Alliance for developing these comprehensive standards and making them publicly available.

## Technology Stack

### Git-Native Implementation

- **Python**: Core language
- **GitPython**: Git integration
- **Click**: CLI framework
- **Rich**: Terminal UI
- **jsonschema**: Metadata validation
- **NetworkX**: Lineage graph analysis
- **pytest**: Testing framework

### Blockchain Implementation

- **Solidity**: Smart contract language
- **Hardhat**: Development environment
- **ethers.js**: Ethereum library
- **OpenZeppelin**: Contract utilities
- **Mocha/Chai**: Testing framework

### Documentation

- **MkDocs**: Documentation generator
- **Material for MkDocs**: Theme
- **Mermaid**: Diagrams
- **GitHub Pages**: Hosting

### Development Tools

- **Nix**: Reproducible environments
- **Docker**: Containerization
- **GitHub Actions**: CI/CD
- **Jupyter**: Interactive notebooks

## Open Source Libraries

This project builds on the shoulders of giants. Special thanks to:

### Python Ecosystem
- Python Software Foundation
- All package maintainers

### Node.js Ecosystem
- Node.js Foundation
- npm package maintainers

### Blockchain Tools
- Ethereum Foundation
- Hardhat team
- OpenZeppelin team

## Examples and Case Studies

The example metadata files in `standards/examples/` are inspired by real-world use cases from:

- **Healthcare**: DICOM standards, HIPAA guidelines
- **ML Training**: HuggingFace datasets, GitHub data
- **IoT**: Sensor network best practices
- **Finance**: PCI-DSS compliance, GDPR requirements

All examples are synthetic/anonymized for educational purposes.

## Documentation Sources

Documentation draws from:

- DTA official specifications
- GDPR regulatory text
- EU AI Act proposals
- FDA guidance on AI/ML
- NIST data management frameworks

## Contributors

This project is maintained by open-source contributors. See [GitHub contributors](https://github.com/Ricoledan/dta-provenance-demo/graphs/contributors) for the full list.

### How to Contribute

We welcome contributions! See our [Contributing Guide](contributing.md) for:
- Code contributions
- Documentation improvements
- Bug reports
- Feature requests
- Example additions

## Inspirations

This project was inspired by:

- **Data provenance research**: Academic work on lineage tracking
- **Version control systems**: Git's elegant design
- **Blockchain projects**: Lessons from failed "blockchain for everything" projects
- **Open source movement**: Commitment to transparency and collaboration

## License

This project is licensed under the **MIT License** - see [LICENSE](license.md) for details.

### DTA Standards License

The Data & Trust Alliance standards are used under their original terms. Please refer to the [official DTA repository](https://github.com/Data-and-Trust-Alliance) for their licensing terms.

## Acknowledgments

Special thanks to:

- The Data & Trust Alliance for developing open standards
- All organizations testing and validating the DTA framework
- Open source maintainers whose tools make this possible
- Early users providing feedback and improvements

## Disclaimer

This project is:
- ✅ An educational demonstration
- ✅ Production-quality code for Git-native approach
- ✅ Open source and freely available

This project is NOT:
- ❌ An official DTA project
- ❌ Legal or compliance advice
- ❌ A complete GDPR/FDA/regulatory solution
- ❌ Financial or professional advice

**Always consult qualified professionals for compliance and legal matters.**

## Contact

- **Issues**: [GitHub Issues](https://github.com/Ricoledan/dta-provenance-demo/issues)
- **Pull Requests**: [GitHub PRs](https://github.com/Ricoledan/dta-provenance-demo/pulls)
- **Documentation**: [Project Website](https://ricoledan.github.io/dta-provenance-demo)

## Citations

If you use this project in academic work, please cite:

```bibtex
@software{dta_provenance_demo,
  title = {DTA Provenance Standards Demo},
  author = {DTA Provenance Demo Contributors},
  year = {2024},
  url = {https://github.com/Ricoledan/dta-provenance-demo},
  note = {Production-quality implementations of Data & Trust Alliance provenance standards}
}
```

And cite the DTA standards:

```bibtex
@techreport{dta_provenance_2023,
  title = {Data Provenance Standards v1.0.0},
  author = {Data and Trust Alliance},
  year = {2023},
  institution = {Data and Trust Alliance},
  url = {https://www.dtaalliance.org/work/data-provenance-standards}
}
```

---

**Thank you to everyone who made this project possible!** 🙏
