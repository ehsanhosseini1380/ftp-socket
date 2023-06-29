import java.util.Scanner;

public class Problem1 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        int n = input.nextInt();
        String first = input.next();
        String second = input.next();
        int count = 0;
        for (int i = 0; i < n; i++) {
            if (first.charAt(i) != second.charAt(i)) {
                count++;
            }
        }
        if ((count%2) != 0) System.out.println("NO");
        else System.out.println(count / 2);
    }
}
