package moderation;
import java.sql.*;

public class SProcedure {

    private static Connection conn = null;

    public static void main(String[] args) throws Exception {
        // Loading the driver
        Class.forName("org.postgresql.Driver");
        // ...connecting to the DB
        conn = DriverManager.getConnection(
                "jdbc:postgresql://localhost/athome",
                "Delilah", "desophie");
        // ...calling moderation function
        moderate(2, 4, 5);
        // ...closing connection.
        conn.close();
    }


    /**
     *
     * @param uid   user id
     * @param aid   activity id
     * @param cid   comment id (=0 if it's activity deletion)
     * @throws SQLException DB error case
     */
    public static void moderate(int uid, int aid, int cid)
            throws SQLException {
        // Statement creation
        CallableStatement stmt
                = conn.prepareCall("{ ? = call Moderation(?,?,?) } ");
        // ...setting parameters
        stmt.registerOutParameter(1, Types.VARCHAR);
        stmt.setInt(2, uid);
        stmt.setInt(3, aid);
        stmt.setInt(4, cid);
        // ... statement execution
        stmt.execute();
        String progress = stmt.getString(1);
        System.out.println(progress);
    }
}