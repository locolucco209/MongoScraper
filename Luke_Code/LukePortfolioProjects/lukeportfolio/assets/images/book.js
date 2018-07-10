// Dependencies
// =============================================================

// Require the sequelize library
const sequelize = Require('sequelize');
// Require the connection to the database (connection.js)
const connection = require('../config/connection.js');

// Create a "Book" model with the following configuration

const book = sequelize.define('book', {
  title: {
    type: Sequelize.STRING
  },
  author: {
    type: Sequelize.STRING
  }
  genre: {
    type: Sequelize.STRING
  }
  pages: {
    type: Sequelize.INTEGER
  }
});

// force: true will drop the table if it already exists
book.sync({force: false}).then(() => {
  // Table created
  return book.create({
    title 'Catcher in Rye',
    author: 'not sure the name',
    genre: 'fiction',
    pages: '200'
  });
});

// 1. A title property of type STRING
// 2. An author property of type STRING
// 3. A genre property of type STRING
// 4. A pages property of type INTEGER
// 5. Set timestamps to false on this model

// Sync model with DB

// Export the book model for other files to use
model.exports = book;
