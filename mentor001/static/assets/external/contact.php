<?php
mb_internal_encoding("UTF-8");
$name = $_POST['name'];
$email = $_POST['email'];
$message = $_POST['message'];

$to = 'your_email_address';
$subject = 'Message From Your Website Contact Form';

$body = "";
$body .= "Name: ";
$body .= $name;
$body .= "\n\n";

$body .= "";
$body .= "Message: ";
$body .= $message;
$body .= "\n";

$headers = 'From: ' .$email . "\r\n";

if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
    mb_send_mail($to, $subject, $body, $headers);
    echo '<span id="valid">Your Email was sent!</span>';
}else{
    echo '<span id="invalid">Your message cannot be sent.</span>';
}
