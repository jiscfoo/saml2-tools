#!/usr/bin/env perl

use strict;
use warnings;

use IO::Uncompress::Inflate qw(inflate $InflateError);
use URI::Escape;
use MIME::Base64;

my $input;
$input .= $_ while <>;
# print "Input data: $input\n";

my $unescaped = uri_unescape($input);
# print "Unescaped data: $unescaped\n";

my $data = decode_base64( $unescaped );
# my @bytes = unpack('C*', pack('H*', $data));
# print "Decoded data: @bytes\n";

my $message = IO::Uncompress::Inflate->new(\$data)
    or die "inflate failed: $InflateError";

print <$message>, "\n";
