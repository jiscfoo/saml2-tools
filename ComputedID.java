import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
// import java.util.Base64;
import javax.xml.bind.DatatypeConverter;

public class ComputedID {

    public enum Encoding {
        /** Use Base64 encoding. */
        BASE64,
        
        /** Use Base32 encoding. */
        BASE32,
    };

    public static void main (String[] args) {
        String SPEntityID = "https://test.ukfederation.org.uk/entity";
        String UserAttribute = null; // = "foo";
        String salt = "...";
        
        byte[] user_bytes = DatatypeConverter.parseBase64Binary("Niu190ehYtzal7NKH0GDGBt1izw=");

        System.out.println(
            generate(
                SPEntityID,
                UserAttribute,
                user_bytes,
                salt,
                null
            )
        );
    }

    public static String generate( 
        final String relyingPartyId, 
        final String sourceId,
        final byte[] sourceId_bytes_in,
        final String salt,
        final byte[] salt_bytes_in) {

        String algorithm = "SHA";
        Encoding encoding = Encoding.BASE64;

        final byte[] sourceId_bytes;
        final byte[] salt_bytes;

        if(salt_bytes_in == null) {
            salt_bytes = salt.getBytes();
        } else {
            salt_bytes = salt_bytes_in;
        }

        if(sourceId_bytes_in == null) {
            sourceId_bytes = sourceId.getBytes();
        } else {
            sourceId_bytes = sourceId_bytes_in;
        }
        
        System.out.println(
            "relyingParty = " + relyingPartyId + "\n" +
            "data = " + (new String(sourceId_bytes)) + 
                " : " + DatatypeConverter.printHexBinary(sourceId_bytes) + 
                " - " + DatatypeConverter.printBase64Binary(sourceId_bytes) + "\n" +
            "salt = " + (new String(salt_bytes)) + 
                " : " + DatatypeConverter.printHexBinary(salt_bytes) + 
                " - " + DatatypeConverter.printBase64Binary(salt_bytes)
            );

        // final byte[] effectiveSalt = getEffectiveSalt(principalName, relyingPartyId);
        // if (effectiveSalt == null) {
        //     throw new RuntimeException("Generation blocked by exception rule");
        // }
        
        try {
            final MessageDigest md = MessageDigest.getInstance(algorithm);
            md.update(relyingPartyId.getBytes());
            md.update((byte) '!');
            md.update(sourceId_bytes);
            md.update((byte) '!');

            // if (encoding == Encoding.BASE32) {
            //     return Base32Support.encode(md.digest(salt_bytes), Base32Support.UNCHUNKED);
            // } else if (encoding == Encoding.BASE64) {
            //     return Base64Support.encode(md.digest(salt_bytes), Base64Support.UNCHUNKED);
            // } else {
            //     throw new SAMLException("Desired encoding was not recognized, unable to compute ID");
            // }

            byte[] digest = md.digest(salt_bytes);

            return DatatypeConverter.printBase64Binary(digest);
        } catch (final NoSuchAlgorithmException e) {
            throw new RuntimeException("Digest algorithm was not supported, unable to compute ID", e);
        }
    }
}