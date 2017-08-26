<?php
mb_internal_encoding("UTF-8");
$name = $_POST['name'];
$email = $_POST['email'];

$to = 'your_email_address';
$subject = 'You Have New Subscriber';

$body = "";
$body .= "Name: ";
$body .= $name;
$body .= "\n\n";

$body .= "Email: ";
$body .= $email;
$body .= "\n\n";

$headers = 'From: ' .$email . "\r\n";

if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
    mb_send_mail($to, $subject, $body, $headers);
    echo '<span id="valid">Thank you for contacting us!</span>';
}else{
    echo '<span id="invalid">Your message cannot be sent.</span>';
}
