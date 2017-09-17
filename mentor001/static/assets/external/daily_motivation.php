<?php
mb_internal_encoding("UTF-8");
$email = $_POST['email'];

$to = 'your_email_address';
$subject = 'You Have New Subscriber on Daily Motivation';

$body .= "Email: ";
$body .= $email;
$body .= "\n\n";

$headers = 'From: ' .$email . "\r\n";

if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
    mb_send_mail($to, $subject, $body, $headers);
    echo 'Thank you for contacting us!';
}else{
    echo 'Your message cannot be sent.';
}
