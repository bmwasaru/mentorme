<?php

$year = date('Y');
$month = date('m');

echo json_encode(array(

    array(
        'id' => 1,
        'date' => "$year-$month-04",
        'title' => "Reserved",
        'classname' => "not-available"
    ),

    array(
        'id' => 2,
        'date' => "$year-$month-10",
        'title' => "Reserved",
        'classname' => "not-available"
    ),

    array(
        'id' => 3,
        'date' => "$year-$month-12",
        'title' => "Reserved",
        'classname' => "not-available"
    ),

    array(
        'id' => 4,
        'date' => "$year-$month-14",
        'title' => "Reserved",
        'classname' => "not-available"
    ),

    array(
        'id' => 5,
        'date' => "$year-$month-26",
        'title' => "Reserved",
        'classname' => "not-available"
    ),

    array(
        'id' => 5,
        'date' => "$year-$month-29",
        'title' => "Reserved",
        'classname' => "not-available"
    )

));

