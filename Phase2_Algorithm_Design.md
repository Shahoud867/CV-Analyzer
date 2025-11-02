# Phase 2: Algorithm Design & Pseudocode Development
## Project: Intelligent CV Analyzer using String Matching Algorithms
### Phase: 2 of 6 | Deliverable: Algorithm Documentation & Pseudocode

---

## 1. Introduction to String Matching Algorithms

String matching algorithms are fundamental tools in computer science for finding occurrences of a pattern within a text. In the context of CV analysis, these algorithms will be used to identify specific skills and keywords within candidate documents.

### 1.1. Problem Definition

Given:
- **Text (T)**: A string of length n representing the CV content
- **Pattern (P)**: A string of length m representing a skill/keyword to find
- **Goal**: Find all occurrences of P in T efficiently

### 1.2. Algorithm Selection Criteria

For CV analysis, we need algorithms that can:
1. Handle case-insensitive matching
2. Process multiple keywords efficiently
3. Provide performance metrics (comparison counts, execution time)
4. Scale well with document size
5. Maintain accuracy in noisy text environments

---

## 2. Algorithm 1: Brute Force (Naive Pattern Matching)

### 2.1. Theoretical Foundation

The Brute Force algorithm is the simplest approach to string matching. It compares the pattern with every possible position in the text, making it easy to understand and implement.

**Core Concept**: For each position i in the text, check if the pattern matches starting at position i.

### 2.2. Algorithm Description

1. **Initialization**: Start with the first character of the text
2. **Comparison**: Compare each character of the pattern with corresponding characters in the text
3. **Advancement**: If a mismatch occurs, move to the next position and repeat
4. **Success**: If all characters match, record the position and continue

### 2.3. Detailed Pseudocode

```
ALGORITHM: BruteForceSearch(T, P)
INPUT: 
    T[0..n-1] - Text string of length n
    P[0..m-1] - Pattern string of length m
OUTPUT: List of positions where pattern occurs

BEGIN
    matches ← empty list
    comparisons ← 0
    
    FOR i = 0 TO n - m DO
        j ← 0
        WHILE j < m AND T[i + j] == P[j] DO
            comparisons ← comparisons + 1
            j ← j + 1
        END WHILE
        
        comparisons ← comparisons + 1  // Count the mismatch comparison
        
        IF j == m THEN
            ADD i TO matches
        END IF
    END FOR
    
    RETURN (matches, comparisons)
END
```

### 2.4. Complexity Analysis

- **Time Complexity**: O(n × m) in worst case
- **Space Complexity**: O(1) additional space
- **Best Case**: O(n) when pattern doesn't occur
- **Average Case**: O(n) for random text

### 2.5. Advantages and Disadvantages

**Advantages**:
- Simple to implement and understand
- No preprocessing required
- Works well for short patterns
- Memory efficient

**Disadvantages**:
- Inefficient for long patterns
- Poor performance on repetitive text
- No optimization for multiple searches

---

## 3. Algorithm 2: Rabin-Karp Algorithm

### 3.1. Theoretical Foundation

The Rabin-Karp algorithm uses hashing to improve efficiency. Instead of comparing characters directly, it compares hash values of the pattern and text substrings.

**Core Concept**: Use rolling hash to compute hash values efficiently and compare patterns based on hash equality.

### 3.2. Algorithm Description

1. **Preprocessing**: Compute hash value of the pattern
2. **Rolling Hash**: Compute hash value of the first m characters of text
3. **Comparison**: Compare hash values; if equal, verify with character-by-character comparison
4. **Rolling**: Update hash value by removing leftmost character and adding rightmost character

### 3.3. Detailed Pseudocode

```
ALGORITHM: RabinKarpSearch(T, P, base, prime)
INPUT: 
    T[0..n-1] - Text string of length n
    P[0..m-1] - Pattern string of length m
    base - Base for hash function (typically 256)
    prime - Prime number for modulo operation
OUTPUT: List of positions where pattern occurs

BEGIN
    matches ← empty list
    comparisons ← 0
    hash_collisions ← 0
    
    // Preprocessing: Calculate hash of pattern
    pattern_hash ← 0
    text_hash ← 0
    h ← 1
    
    // Calculate h = base^(m-1) mod prime
    FOR i = 0 TO m - 2 DO
        h ← (h * base) mod prime
    END FOR
    
    // Calculate initial hash values
    FOR i = 0 TO m - 1 DO
        pattern_hash ← (base * pattern_hash + P[i]) mod prime
        text_hash ← (base * text_hash + T[i]) mod prime
    END FOR
    
    // Slide the pattern over text
    FOR i = 0 TO n - m DO
        // Check if hash values match
        IF pattern_hash == text_hash THEN
            // Verify with character-by-character comparison
            j ← 0
            WHILE j < m AND T[i + j] == P[j] DO
                comparisons ← comparisons + 1
                j ← j + 1
            END WHILE
            
            comparisons ← comparisons + 1  // Count the mismatch comparison
            
            IF j == m THEN
                ADD i TO matches
            ELSE
                hash_collisions ← hash_collisions + 1
            END IF
        END IF
        
        // Calculate hash for next window
        IF i < n - m THEN
            text_hash ← (base * (text_hash - T[i] * h) + T[i + m]) mod prime
            // Ensure positive hash value
            IF text_hash < 0 THEN
                text_hash ← text_hash + prime
            END IF
        END IF
    END FOR
    
    RETURN (matches, comparisons, hash_collisions)
END
```

### 3.4. Complexity Analysis

- **Time Complexity**: O(n + m) average case, O(n × m) worst case
- **Space Complexity**: O(1) additional space
- **Best Case**: O(n + m) when no hash collisions occur
- **Average Case**: O(n + m) with good hash function

### 3.5. Advantages and Disadvantages

**Advantages**:
- Good average-case performance
- Can be extended for multiple patterns
- Hash-based optimization reduces comparisons
- Suitable for large texts

**Disadvantages**:
- Worst-case performance same as brute force
- Hash collisions can degrade performance
- Requires careful choice of hash parameters

---

## 4. Algorithm 3: Knuth-Morris-Pratt (KMP) Algorithm

### 4.1. Theoretical Foundation

The KMP algorithm uses information from previous comparisons to avoid redundant work. It preprocesses the pattern to create a failure function that indicates where to resume matching after a mismatch.

**Core Concept**: When a mismatch occurs, use the failure function to determine the next position to check, avoiding backtracking in the text.

### 4.2. Algorithm Description

1. **Preprocessing**: Build failure function (LPS array) for the pattern
2. **Matching**: Use failure function to optimize pattern matching
3. **Failure Function**: For each position, find the longest proper prefix that is also a suffix

### 4.3. Detailed Pseudocode

```
ALGORITHM: KMPSearch(T, P)
INPUT: 
    T[0..n-1] - Text string of length n
    P[0..m-1] - Pattern string of length m
OUTPUT: List of positions where pattern occurs

BEGIN
    matches ← empty list
    comparisons ← 0
    
    // Build failure function (LPS array)
    lps ← BuildFailureFunction(P)
    
    i ← 0  // Index for text
    j ← 0  // Index for pattern
    
    WHILE i < n DO
        IF T[i] == P[j] THEN
            comparisons ← comparisons + 1
            i ← i + 1
            j ← j + 1
        END IF
        
        IF j == m THEN
            ADD (i - j) TO matches
            j ← lps[j - 1]
        ELSE IF i < n AND T[i] != P[j] THEN
            comparisons ← comparisons + 1
            IF j != 0 THEN
                j ← lps[j - 1]
            ELSE
                i ← i + 1
            END IF
        END IF
    END WHILE
    
    RETURN (matches, comparisons)
END

ALGORITHM: BuildFailureFunction(P)
INPUT: P[0..m-1] - Pattern string
OUTPUT: LPS array (Longest Proper Suffix)

BEGIN
    m ← length of P
    lps[0..m-1] ← array initialized to 0
    len ← 0  // Length of previous longest prefix suffix
    i ← 1
    
    WHILE i < m DO
        IF P[i] == P[len] THEN
            len ← len + 1
            lps[i] ← len
            i ← i + 1
        ELSE
            IF len != 0 THEN
                len ← lps[len - 1]
            ELSE
                lps[i] ← 0
                i ← i + 1
            END IF
        END IF
    END WHILE
    
    RETURN lps
END
```

### 4.4. Complexity Analysis

- **Time Complexity**: O(n + m) for both preprocessing and matching
- **Space Complexity**: O(m) for the failure function
- **Best Case**: O(n + m)
- **Worst Case**: O(n + m)

### 4.5. Advantages and Disadvantages

**Advantages**:
- Guaranteed linear time complexity
- No backtracking in text
- Optimal for single pattern matching
- Predictable performance

**Disadvantages**:
- Requires preprocessing time
- Additional memory for failure function
- More complex to implement
- Overhead for short patterns

---

## 5. Algorithm Comparison and Analysis

### 5.1. Performance Comparison Table

| Algorithm | Time Complexity | Space Complexity | Preprocessing | Best Use Case |
|-----------|----------------|------------------|---------------|---------------|
| **Brute Force** | O(n×m) | O(1) | None | Short patterns, simple implementation |
| **Rabin-Karp** | O(n+m) avg, O(n×m) worst | O(1) | O(m) | Multiple patterns, large texts |
| **KMP** | O(n+m) | O(m) | O(m) | Single pattern, guaranteed performance |

### 5.2. Detailed Performance Characteristics

#### 5.2.1. Execution Time Analysis

**Small Documents (1-5 KB)**:
- Brute Force: Fastest due to no preprocessing
- Rabin-Karp: Moderate overhead from hashing
- KMP: Overhead from failure function construction

**Medium Documents (5-50 KB)**:
- KMP: Best performance due to linear complexity
- Rabin-Karp: Good performance with minimal hash collisions
- Brute Force: Performance degrades with pattern length

**Large Documents (50+ KB)**:
- KMP: Consistently best performance
- Rabin-Karp: Good performance, depends on hash quality
- Brute Force: Significantly slower

#### 5.2.2. Memory Usage Analysis

**Brute Force**: Minimal memory footprint
**Rabin-Karp**: Minimal memory footprint
**KMP**: Additional O(m) space for failure function

#### 5.2.3. Comparison Count Analysis

**Brute Force**: High comparison count, especially with repetitive patterns
**Rabin-Karp**: Reduced comparisons due to hash filtering
**KMP**: Minimal comparisons due to failure function optimization

### 5.3. CV Analysis Specific Considerations

#### 5.3.1. Keyword Characteristics in CVs

**Short Keywords (1-3 characters)**: "AI", "ML", "DB"
- Brute Force performs well
- KMP overhead may not be justified

**Medium Keywords (4-10 characters)**: "Python", "React", "Testing"
- KMP shows clear advantage
- Rabin-Karp provides good balance

**Long Keywords (10+ characters)**: "Machine Learning", "Software Testing"
- KMP significantly outperforms others
- Brute Force becomes inefficient

#### 5.3.2. Text Characteristics

**Technical CVs**: High keyword density, repetitive terms
- KMP excels due to pattern repetition
- Rabin-Karp benefits from hash optimization

**General CVs**: Mixed content, varied terminology
- All algorithms perform reasonably well
- KMP maintains consistent performance

**Noisy Text**: OCR errors, formatting issues
- Brute Force most robust to errors
- KMP may fail on corrupted patterns

---

## 6. Implementation Considerations for CV Analysis

### 6.1. Case-Insensitive Matching

All algorithms need modification for case-insensitive matching:

```
MODIFICATION: Case-Insensitive Comparison
FOR each character comparison:
    IF toLowerCase(T[i]) == toLowerCase(P[j]) THEN
        // Characters match
    ELSE
        // Characters don't match
    END IF
```

### 6.2. Multiple Keyword Handling

**Sequential Approach**:
```
FOR each keyword in job_description:
    results ← algorithm.search(cv_text, keyword)
    aggregate_results(results)
```

**Parallel Approach**:
```
spawn_threads_for_each_keyword()
wait_for_all_completions()
merge_results()
```

### 6.3. Performance Monitoring

**Metrics to Track**:
- Execution time per algorithm
- Total comparisons made
- Memory usage
- Hash collisions (Rabin-Karp)
- Failure function construction time (KMP)

### 6.4. Error Handling

**File Processing Errors**:
- Corrupted files
- Unsupported formats
- Empty files
- Encoding issues

**Algorithm Errors**:
- Pattern length validation
- Text length validation
- Memory allocation failures
- Integer overflow (hash calculations)

---

## 7. Expected Performance in CV Analysis Context

### 7.1. Typical CV Characteristics

**Average CV Size**: 2-5 pages (5-15 KB text)
**Keyword Count**: 10-50 skills per job description
**Pattern Length**: 3-20 characters per keyword

### 7.2. Performance Projections

**Small CV (5 KB, 20 keywords)**:
- Brute Force: ~0.1 seconds
- Rabin-Karp: ~0.05 seconds
- KMP: ~0.03 seconds

**Medium CV (15 KB, 30 keywords)**:
- Brute Force: ~0.5 seconds
- Rabin-Karp: ~0.2 seconds
- KMP: ~0.1 seconds

**Large CV (50 KB, 50 keywords)**:
- Brute Force: ~3.0 seconds
- Rabin-Karp: ~0.8 seconds
- KMP: ~0.3 seconds

### 7.3. Scalability Analysis

**Batch Processing (100 CVs)**:
- Brute Force: May become impractical
- Rabin-Karp: Good performance with parallel processing
- KMP: Excellent performance, scales linearly

---

## 8. Algorithm Selection Recommendations

### 8.1. For Different Use Cases

**Real-time Analysis** (Single CV):
- **Recommended**: KMP
- **Reason**: Consistent performance, predictable timing

**Batch Processing** (Multiple CVs):
- **Recommended**: Rabin-Karp with parallel processing
- **Reason**: Good balance of performance and memory usage

**Educational/Demonstration**:
- **Recommended**: All three algorithms
- **Reason**: Shows performance differences and trade-offs

### 8.2. Hybrid Approach

**Optimal Strategy**:
1. Use KMP for long keywords (>10 characters)
2. Use Rabin-Karp for medium keywords (4-10 characters)
3. Use Brute Force for short keywords (<4 characters)

**Implementation**:
```
IF keyword_length < 4 THEN
    algorithm ← BruteForce
ELSE IF keyword_length < 10 THEN
    algorithm ← RabinKarp
ELSE
    algorithm ← KMP
END IF
```

---

## 9. Conclusion

### 9.1. Algorithm Summary

Each algorithm has distinct advantages:

- **Brute Force**: Simple, reliable baseline
- **Rabin-Karp**: Good average performance, extensible
- **KMP**: Optimal performance, guaranteed linear time

### 9.2. Implementation Readiness

The pseudocode provided is ready for implementation in Phase 3. Key considerations:

1. **Error Handling**: Robust input validation
2. **Performance Monitoring**: Comprehensive metrics collection
3. **Memory Management**: Efficient data structures
4. **Scalability**: Support for large document processing

### 9.3. Next Phase Preparation

Phase 2 has established the theoretical foundation and implementation roadmap. Phase 3 will focus on:

1. **Python Implementation**: Converting pseudocode to working code
2. **Integration**: Building the unified analyzer framework
3. **Testing**: Unit tests and validation
4. **Optimization**: Performance tuning and error handling

---

**Phase 2 Complete** ✅

**Deliverables Produced**:
- Comprehensive algorithm documentation
- Detailed pseudocode for all three algorithms
- Performance comparison and analysis
- Implementation considerations and recommendations
- Scalability analysis and projections
- Algorithm selection guidelines

👉 **Type continue to move to the next phase.**
