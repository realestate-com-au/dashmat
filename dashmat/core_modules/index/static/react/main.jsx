import React, {Component, PropTypes} from 'react';
import {Jumbotron} from 'react-bootstrap';
import styles from './Index.css';

export class Index extends Component {
  render() {
    return (
      <Jumbotron className={styles.index_container}>
        {this.props.children}
      </Jumbotron>
    );
  }
}

Index.propTypes = {
  children: PropTypes.array,
};

export class IndexItem extends Component {
  render() {
    return (
      <p>
        <a href={this.props.href}>{this.props.desc}</a>
      </p>
    );
  }
}

IndexItem.propTypes = {
  desc: PropTypes.string,
  href: PropTypes.string,
};

