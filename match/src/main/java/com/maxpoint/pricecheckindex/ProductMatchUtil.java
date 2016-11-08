package com.maxpoint.pricecheckindex;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ProductMatchUtil {
    /**
     * Determine similarity based on jaccard index
     * @param p1
     * @param p2
     * @return
     */
    public static String getSimilarity (String p1, String p2) {
        double jaccardIndex = getJaccardIndex(p1, p2);

        if (jaccardIndex >= 0.80) {
            return "Same";
        } else if (jaccardIndex >= 0.5) {
            return "Similar";
        } else {
            return "Different";
        }
    }

    /**
     * Equation for Jaccard Index is interscation of 2 arrays / their union
     * It's useful for determining the similarity of 2 arrays
     * @param p1
     * @param p2
     * @return
     */
    public static double getJaccardIndex(String p1, String p2) {
        String[] arr1 = strToArray(p1);
        String[] arr2 = strToArray(p2);

        Set<String> mySet = new HashSet<String>(Arrays.asList(arr1));
        int interscation = 0;
        int extra = 0;
        for (String s : arr2) {
            if (mySet.contains(s)) {
                interscation++;
            } else {
                extra++;
            }
        }

        int union = (arr1.length > arr2.length ? arr1.length : arr2.length) + extra;
        double jaccardIndex = (double) interscation / union;

        jaccardIndex += getJaccardBooster(getCountNumber(p1), getCountNumber(p2));
        return jaccardIndex;
    }

    /**
     * Clean string, then breaks it into token for calculating jaccard index
     * @param str
     * @return
     */
    public static String[] strToArray(String str) {
        String s = str.toLowerCase().trim().replaceAll("(\\s)-(\\s)", " ");
        s = s.trim().replaceAll("[®-]", " ");
        s = s.replaceAll("\\(.*\\)", "");
        return s.split(" ");
    }

    /**
     * If 2 products contains the same unit count (ex. 2 rolls), give them a booster score
     * @param s1
     * @param s2
     * @return
     */
    public static double getJaccardBooster(Set<String> s1, Set<String> s2) {
        int count = 0;
        for (String s : s1) {
            if (s2.contains(s))
                count++;
        }
        return count * 0.3;
    }

    public static Set<String> getCountNumber(String productName) {
        String line = "\\d+ (\\w)*";
        Pattern r = Pattern.compile(line);
        Matcher m = r.matcher(productName);

        Set<String> countSet = new HashSet<String>();

        while(m.find()) {
            countSet.add(m.group().toLowerCase());
        }

        return countSet;
    }
}
