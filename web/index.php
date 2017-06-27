<?php

//
// Author: Daniel Abercrombie <dabercro@mit.edu>
//

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
mysqli_report(MYSQLI_REPORT_STRICT);

// Get the parameters and take a guess whether or not this is in a browser

$sample = isset($_GET['sample']) ? $_GET['sample'] : '';
$inbrowser = isset($_GET['browse']) || $sample === '';
$energy = isset($_GET['energy']) ? $_GET['energy'] : '13';
$history = isset($_GET['history']);

// Make sure we use a valid table

if (! in_array($energy, array('7', '8', '13', '14')))
  die('Invalid energy: ' . $energy);

$table = 'xs_' . $energy . 'TeV';

if ($history)
  $table = $table . '_history';

// Connect to MySQL database

$ini_file = isset($_SERVER['XSECCONF'])? $_SERVER['XSECCONF'] : '/home/dabercro/xsec.cnf';
$config = parse_ini_file($ini_file, true);
$user_params = $config['mysql-crosssec-reader'];

$user = $user_params['user'];
$server = $user_params['host'];
$passwd = $user_params['password'];

$conn = new mysqli($server, $user, $passwd, 'cross_sections');

if ($conn->connect_error)
  die('Connection failed: ' . $conn->connect_error);

// Rest of behavior is determined by browser

if ($inbrowser) {

  // If the history is not viewed, get the list of samples that have a history
  $updated = array();
  if (! $history) {
    $check_history = $conn->query('SELECT sample FROM ' . $table .
                                  '_history GROUP BY sample HAVING COUNT(*) > 1');

    while($row = $check_history->fetch_assoc())
      array_push($updated, $row['sample']);

  }

  // Get all the entries in the database, and then perform regex matching.
  // Matching happens in the body.

  $result = $conn->query('SELECT sample, cross_section, uncertainty, last_updated, source, comments FROM ' .
                         $table . ' ORDER BY sample ASC, last_updated DESC');

  include 'body.html';

} else {

  // Get single sample, and return it

  $stmt = $conn->prepare('SELECT cross_section FROM ' . $table . ' WHERE sample=?');

  $stmt->bind_param('s', $sample);
  $stmt->execute();
  $stmt->bind_result($xs);
  $stmt->fetch();
  $stmt->close();

  if ($xs)
    echo $xs;
  else
    printf('ERROR: cross section missing for %s at energy %s TeV.', $sample, $energy);

}

$conn->close();

?>
