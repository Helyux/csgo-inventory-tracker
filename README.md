<div id="top">
<!-- src: https://github.com/othneildrew/Best-README-Template -->
</div>


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Helyux/csgo-inventory-tracker">
    <img src="images/logo.png" alt="Logo" width="725" height="88">
  </a>

  <h3 align="center">csgo-inventory-tracker</h3>

  <p align="center">
    create your own inventory tracker.
    <br />
    <a href="https://github.com/Helyux/csgo-inventory-tracker">View Demo</a>
    ·
    <a href="https://github.com/Helyux/csgo-inventory-tracker/issues">Report Bug</a>
    ·
    <a href="https://github.com/Helyux/csgo-inventory-tracker/issues">Request Feature</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites :airplane:</a></li>
        <li><a href="#SQL Configuration">SQL Configuration :wrench:</a></li>
        <li><a href="#installation">Installation :zap:</a></li>
        <li><a href="#configuration">Configuration :clipboard:</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

blah blah inventory tracking blah blah

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites :airplane:

* MySQL Server
  ```sh
  sudo apt update
  sudo apt install mysql-server
  sudo mysql_secure_installation
  ```

### SQL Configuration :wrench:

1. Login as root
  ```sh
  mysql -u root -p
  ```

2. Create a SQL User
  ```sh
  CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';`
  ```

3. Setup a SQL Database
  ```sh
  CREATE DATABASE IF NOT EXISTS databasename;
  ```

4. Grant all rights for the created user to the created database
  ```sh
  GRANT ALL PRIVILEGES ON databasename.* TO 'username'@'localhost';
  ```

5. Flush privileges
  ```sh
  FLUSH PRIVILEGES;
  ```

### Installation :zap:

1. Clone the repository
   ```sh
   git clone https://github.com/Helyux/csgo-inventory-tracker
   ```
2. Install python packages from pipfile
   ```sh
   pipenv install
   ```
3. Run the entry script
   ```sh
   pipenv run python main.py
   ```

### Configuration  :clipboard:
1. Make a copy of template.toml named prod.toml in the base directory
2. Fill in the variables in prod.toml

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [ ] make the use of proxys to counter ratelimiting possible

See the [open issues](https://github.com/Helyux/csgo-inventory-tracker/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the GPL-3.0 License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Lukas Mahler - [@LyuxGG](https://twitter.com/LyuxGG) - m@hler.eu

Project Link: [https://github.com/Helyux/csgo-inventory-tracker](https://github.com/Helyux/csgo-inventory-tracker)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [Img Shields](https://shields.io)
* [Logo Generator](https://creecros.github.io/simple_logo_gen)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Helyux/csgo-inventory-tracker.svg?style=for-the-badge
[contributors-url]: https://github.com/Helyux/csgo-inventory-tracker/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Helyux/csgo-inventory-tracker.svg?style=for-the-badge
[forks-url]: https://github.com/Helyux/csgo-inventory-tracker/network/members
[stars-shield]: https://img.shields.io/github/stars/Helyux/csgo-inventory-tracker.svg?style=for-the-badge
[stars-url]: https://github.com/Helyux/csgo-inventory-tracker/stargazers
[issues-shield]: https://img.shields.io/github/issues/Helyux/csgo-inventory-tracker.svg?style=for-the-badge
[issues-url]: https://github.com/Helyux/csgo-inventory-tracker/issues
[license-shield]: https://img.shields.io/github/license/Helyux/csgo-inventory-tracker.svg?style=for-the-badge
[license-url]: https://github.com/Helyux/csgo-inventory-tracker/blob/master/LICENSE.txt
